import requests
import jwt
import time
import uuid
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import TelehealthSession, TelehealthParticipant
import logging

logger = logging.getLogger(__name__)


class TelehealthPlatformService:
    """Service for managing different telehealth platforms"""
    
    def create_session(self, patient, provider, scheduled_start, scheduled_end, platform=None):
        """Create a telehealth session based on user tier"""
        
        # Determine platform based on subscription tier
        if platform is None:
            if provider.can_use_zoom:
                platform = 'zoom'
            else:
                platform = 'webrtc'
        
        # Generate unique room name
        room_name = f"session_{uuid.uuid4().hex[:8]}"
        
        session = TelehealthSession.objects.create(
            room_name=room_name,
            patient=patient,
            provider=provider,
            platform=platform,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end
        )
        
        # Configure platform-specific settings
        if platform == 'zoom':
            zoom_service = ZoomService()
            zoom_config = zoom_service.create_meeting(session)
            session.zoom_meeting_id = zoom_config.get('meeting_id')
            session.zoom_meeting_password = zoom_config.get('password')
            session.zoom_join_url = zoom_config.get('join_url')
        elif platform == 'webrtc':
            webrtc_service = WebRTCService()
            webrtc_config = webrtc_service.create_room(session)
            session.webrtc_room_config = webrtc_config
        elif platform == 'jitsi':
            jitsi_service = JitsiService()
            jitsi_config = jitsi_service.create_room(session)
            session.jitsi_room_url = jitsi_config.get('room_url')
        
        session.save()
        
        # Create participant records
        TelehealthParticipant.objects.create(
            session=session,
            user=patient,
            role='patient',
            can_share_screen=False,
            can_record=False
        )
        TelehealthParticipant.objects.create(
            session=session,
            user=provider,
            role='provider',
            can_share_screen=True,
            can_record=True,
            is_moderator=True
        )
        
        return session
    
    def join_session(self, session, user):
        """Handle user joining a session"""
        try:
            participant = TelehealthParticipant.objects.get(
                session=session,
                user=user
            )
            
            if session.platform == 'zoom':
                zoom_service = ZoomService()
                join_info = zoom_service.get_join_info(session, user)
            elif session.platform == 'webrtc':
                webrtc_service = WebRTCService()
                join_info = webrtc_service.get_join_info(session, user)
            elif session.platform == 'jitsi':
                jitsi_service = JitsiService()
                join_info = jitsi_service.get_join_info(session, user)
            else:
                raise ValueError(f"Unsupported platform: {session.platform}")
            
            # Update participant status
            participant.joined_at = timezone.now()
            participant.connection_id = join_info.get('connection_id', str(uuid.uuid4()))
            participant.save()
            
            # Update session status if first participant
            if session.status == 'scheduled':
                session.status = 'waiting'
                session.save()
            
            return join_info
            
        except TelehealthParticipant.DoesNotExist:
            raise ValueError("User is not authorized to join this session")
    
    def leave_session(self, session, user):
        """Handle user leaving a session"""
        try:
            participant = TelehealthParticipant.objects.get(
                session=session,
                user=user
            )
            
            participant.left_at = timezone.now()
            participant.save()
            
            # Check if all participants have left
            remaining_participants = session.participants.filter(left_at__isnull=True)
            if not remaining_participants.exists():
                session.status = 'ended'
                session.actual_end = timezone.now()
                session.save()
            
        except TelehealthParticipant.DoesNotExist:
            pass  # User wasn't in session


class ZoomService:
    """Zoom SDK integration service"""
    
    def __init__(self):
        self.api_key = settings.ZOOM_API_KEY
        self.api_secret = settings.ZOOM_API_SECRET
        self.base_url = 'https://api.zoom.us/v2'
    
    def _generate_jwt(self):
        """Generate JWT token for Zoom API authentication"""
        header = {'alg': 'HS256', 'typ': 'JWT'}
        
        payload = {
            'iss': self.api_key,
            'exp': int(time.time() + 3600)  # Token expires in 1 hour
        }
        
        token = jwt.encode(payload, self.api_secret, algorithm='HS256', headers=header)
        return token
    
    def create_meeting(self, session):
        """Create a Zoom meeting"""
        try:
            token = self._generate_jwt()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            meeting_data = {
                'topic': f'Telehealth Session - {session.patient.full_name}',
                'type': 2,  # Scheduled meeting
                'start_time': session.scheduled_start.isoformat(),
                'duration': int((session.scheduled_end - session.scheduled_start).total_seconds() / 60),
                'timezone': 'UTC',
                'password': self._generate_meeting_password(),
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'cn_meeting': False,
                    'in_meeting': False,
                    'join_before_host': False,
                    'mute_upon_entry': True,
                    'watermark': False,
                    'use_pmi': False,
                    'approval_type': 2,  # Manual approval
                    'audio': 'both',
                    'auto_recording': 'none',
                    'waiting_room': True
                }
            }
            
            response = requests.post(
                f'{self.base_url}/users/me/meetings',
                json=meeting_data,
                headers=headers
            )
            
            if response.status_code == 201:
                meeting_info = response.json()
                return {
                    'meeting_id': meeting_info['id'],
                    'password': meeting_info['password'],
                    'join_url': meeting_info['join_url'],
                    'start_url': meeting_info['start_url']
                }
            else:
                logger.error(f"Failed to create Zoom meeting: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Zoom meeting: {str(e)}")
            return None
    
    def get_join_info(self, session, user):
        """Get join information for a user"""
        if user == session.provider:
            # Provider gets host URL
            return {
                'platform': 'zoom',
                'join_url': session.zoom_join_url,
                'meeting_id': session.zoom_meeting_id,
                'password': session.zoom_meeting_password,
                'role': 'host',
                'connection_id': f"zoom_{session.zoom_meeting_id}_{user.id}"
            }
        else:
            # Patient gets participant URL
            return {
                'platform': 'zoom',
                'join_url': session.zoom_join_url,
                'meeting_id': session.zoom_meeting_id,
                'password': session.zoom_meeting_password,
                'role': 'participant',
                'connection_id': f"zoom_{session.zoom_meeting_id}_{user.id}"
            }
    
    def _generate_meeting_password(self):
        """Generate a secure meeting password"""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


class WebRTCService:
    """WebRTC service for free tier users"""
    
    def __init__(self):
        self.stun_servers = settings.WEBRTC_STUN_SERVERS
        self.turn_servers = getattr(settings, 'WEBRTC_TURN_SERVERS', [])
    
    def create_room(self, session):
        """Create WebRTC room configuration"""
        room_config = {
            'room_id': session.room_name,
            'ice_servers': self._get_ice_servers(),
            'constraints': {
                'video': True,
                'audio': True
            },
            'codec_preferences': ['VP8', 'H264'],
            'bandwidth_limits': {
                'video': 500000,  # 500 kbps
                'audio': 64000    # 64 kbps
            }
        }
        
        return room_config
    
    def get_join_info(self, session, user):
        """Get WebRTC join information"""
        participant = TelehealthParticipant.objects.get(session=session, user=user)
        
        return {
            'platform': 'webrtc',
            'room_id': session.room_name,
            'ice_servers': self._get_ice_servers(),
            'user_id': str(user.id),
            'display_name': user.full_name,
            'role': participant.role,
            'permissions': {
                'can_share_screen': participant.can_share_screen,
                'can_record': participant.can_record,
                'is_moderator': participant.is_moderator
            },
            'connection_id': f"webrtc_{session.room_name}_{user.id}"
        }
    
    def _get_ice_servers(self):
        """Get ICE servers configuration"""
        ice_servers = []
        
        # Add STUN servers
        for stun_server in self.stun_servers:
            ice_servers.append({
                'urls': stun_server
            })
        
        # Add TURN servers if available
        for turn_server in self.turn_servers:
            ice_servers.append({
                'urls': turn_server['url'],
                'username': turn_server.get('username'),
                'credential': turn_server.get('credential')
            })
        
        return ice_servers


class JitsiService:
    """Jitsi Meet integration service"""
    
    def __init__(self):
        self.server_url = settings.JITSI_SERVER_URL
    
    def create_room(self, session):
        """Create Jitsi room"""
        room_name = session.room_name
        room_url = f"{self.server_url}/{room_name}"
        
        return {
            'room_url': room_url,
            'room_name': room_name
        }
    
    def get_join_info(self, session, user):
        """Get Jitsi join information"""
        participant = TelehealthParticipant.objects.get(session=session, user=user)
        
        # Build Jitsi URL with parameters
        params = {
            'displayName': user.full_name,
            'userId': str(user.id),
            'role': participant.role
        }
        
        # Add moderator settings for providers
        if participant.is_moderator:
            params['isModerator'] = 'true'
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        join_url = f"{session.jitsi_room_url}#{query_string}"
        
        return {
            'platform': 'jitsi',
            'join_url': join_url,
            'room_name': session.room_name,
            'display_name': user.full_name,
            'role': participant.role,
            'connection_id': f"jitsi_{session.room_name}_{user.id}"
        }


class TelehealthNotificationService:
    """Service for sending telehealth-related notifications"""
    
    def send_session_reminder(self, session, minutes_before=15):
        """Send reminder notification before session"""
        from apps.notifications.services import NotificationService
        
        notification_service = NotificationService()
        
        # Send to patient
        notification_service.send_notification(
            user=session.patient,
            title='Upcoming Telehealth Session',
            message=f'Your telehealth appointment with {session.provider.full_name} starts in {minutes_before} minutes.',
            notification_type='telehealth_reminder',
            data={
                'session_id': str(session.session_id),
                'provider_name': session.provider.full_name,
                'scheduled_start': session.scheduled_start.isoformat()
            }
        )
        
        # Send to provider
        notification_service.send_notification(
            user=session.provider,
            title='Upcoming Telehealth Session',
            message=f'Your telehealth appointment with {session.patient.full_name} starts in {minutes_before} minutes.',
            notification_type='telehealth_reminder',
            data={
                'session_id': str(session.session_id),
                'patient_name': session.patient.full_name,
                'scheduled_start': session.scheduled_start.isoformat()
            }
        )
    
    def send_session_invitation(self, session):
        """Send session invitation with join link"""
        from apps.notifications.services import NotificationService
        
        notification_service = NotificationService()
        
        # Create join links based on platform
        if session.platform == 'zoom':
            join_link = session.zoom_join_url
        elif session.platform == 'jitsi':
            join_link = session.jitsi_room_url
        else:
            join_link = f"/telehealth/session/{session.session_id}/join"
        
        # Send to patient
        notification_service.send_notification(
            user=session.patient,
            title='Telehealth Session Scheduled',
            message=f'A telehealth session has been scheduled with {session.provider.full_name} on {session.scheduled_start.strftime("%B %d, %Y at %I:%M %p")}.',
            notification_type='telehealth_invitation',
            data={
                'session_id': str(session.session_id),
                'join_link': join_link,
                'platform': session.platform
            }
        )