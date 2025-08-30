from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    TelehealthSession, TelehealthParticipant, WebRTCSignaling,
    TelehealthDeviceTest, TelehealthRecording, TelehealthWaitingRoom
)
from .clinic_models import ClinicSettings, TelehealthTierAuditLog, TelehealthUsageAnalytics
from .serializers import (
    TelehealthSessionSerializer, TelehealthParticipantSerializer,
    WebRTCSignalingSerializer, TelehealthDeviceTestSerializer,
    TelehealthRecordingSerializer, SessionJoinInfoSerializer,
    TelehealthWaitingRoomSerializer, ClinicSettingsSerializer,
    TelehealthTierAuditLogSerializer, TelehealthUsageAnalyticsSerializer,
    TelehealthTierPreviewSerializer
)
from .services import TelehealthPlatformService, TelehealthNotificationService
from apps.authentication.models import AuditLog


class TelehealthSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for telehealth sessions"""
    
    serializer_class = TelehealthSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            return TelehealthSession.objects.filter(patient=user)
        elif user.user_type in ['provider', 'care_team']:
            return TelehealthSession.objects.filter(
                Q(provider=user) | Q(participants__user=user)
            ).distinct()
        else:
            return TelehealthSession.objects.none()
    
    def perform_create(self, serializer):
        """Create telehealth session with platform setup"""
        session = serializer.save()
        
        # Set up platform-specific configuration
        platform_service = TelehealthPlatformService()
        platform_service.create_session(
            session.patient,
            session.provider,
            session.scheduled_start,
            session.scheduled_end,
            session.platform
        )
        
        # Send invitation notifications
        notification_service = TelehealthNotificationService()
        notification_service.send_session_invitation(session)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a telehealth session"""
        session = self.get_object()
        user = request.user
        
        try:
            platform_service = TelehealthPlatformService()
            join_info = platform_service.join_session(session, user)
            
            serializer = SessionJoinInfoSerializer(join_info)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a telehealth session"""
        session = self.get_object()
        user = request.user
        
        platform_service = TelehealthPlatformService()
        platform_service.leave_session(session, user)
        
        return Response({'message': 'Left session successfully'})
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a telehealth session"""
        session = self.get_object()
        
        if session.status != 'scheduled':
            return Response(
                {'error': 'Session cannot be started in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'active'
        session.actual_start = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a telehealth session"""
        session = self.get_object()
        
        if session.status not in ['active', 'waiting']:
            return Response(
                {'error': 'Session cannot be ended in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'ended'
        session.actual_end = timezone.now()
        session.save()
        
        # Update all participants
        session.participants.filter(left_at__isnull=True).update(
            left_at=timezone.now()
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming sessions"""
        now = timezone.now()
        sessions = self.get_queryset().filter(
            scheduled_start__gte=now,
            status__in=['scheduled', 'waiting']
        ).order_by('scheduled_start')[:10]
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's sessions"""
        today = timezone.now().date()
        sessions = self.get_queryset().filter(
            scheduled_start__date=today
        ).order_by('scheduled_start')
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)


class TelehealthDeviceTestViewSet(viewsets.ModelViewSet):
    """ViewSet for device tests"""
    
    serializer_class = TelehealthDeviceTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TelehealthDeviceTest.objects.filter(user=self.request.user).order_by('-tested_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def run_full_test(self, request):
        """Run a comprehensive device and network test"""
        user = request.user
        session_id = request.data.get('session_id')
        
        session = None
        if session_id:
            try:
                session = TelehealthSession.objects.get(
                    session_id=session_id,
                    participants__user=user
                )
            except TelehealthSession.DoesNotExist:
                pass
        
        # Simulate comprehensive test results
        test_results = []
        
        # Microphone test
        mic_test = TelehealthDeviceTest.objects.create(
            user=user,
            session=session,
            test_type='microphone',
            test_result='pass',
            details={'audio_level': 0.8, 'noise_level': 0.1}
        )
        test_results.append(self.get_serializer(mic_test).data)
        
        # Camera test
        camera_test = TelehealthDeviceTest.objects.create(
            user=user,
            session=session,
            test_type='camera',
            test_result='pass',
            details={'resolution': '1280x720', 'fps': 30}
        )
        test_results.append(self.get_serializer(camera_test).data)
        
        # Network test
        network_test = TelehealthDeviceTest.objects.create(
            user=user,
            session=session,
            test_type='network',
            test_result='pass',
            upload_speed_mbps=25.5,
            download_speed_mbps=50.2,
            latency_ms=45,
            packet_loss_percent=0.1,
            details={'connection_type': 'wifi', 'signal_strength': 'excellent'}
        )
        test_results.append(self.get_serializer(network_test).data)
        
        return Response({
            'message': 'Device tests completed',
            'results': test_results,
            'overall_status': 'pass'
        })


class WebRTCSignalingViewSet(viewsets.ModelViewSet):
    """ViewSet for WebRTC signaling"""
    
    serializer_class = WebRTCSignalingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        session_id = self.request.query_params.get('session_id')
        
        queryset = WebRTCSignaling.objects.filter(
            Q(sender=user) | Q(receiver=user) | Q(receiver__isnull=True)
        )
        
        if session_id:
            queryset = queryset.filter(session__session_id=session_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending signaling messages for user"""
        user = request.user
        session_id = request.query_params.get('session_id')
        
        queryset = WebRTCSignaling.objects.filter(
            Q(receiver=user) | Q(receiver__isnull=True),
            processed=False
        )
        
        if session_id:
            queryset = queryset.filter(session__session_id=session_id)
        
        messages = queryset.order_by('created_at')
        
        # Mark as processed
        messages.update(processed=True)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class TelehealthRecordingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for session recordings (read-only)"""
    
    serializer_class = TelehealthRecordingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            return TelehealthRecording.objects.filter(
                session__patient=user,
                status='completed'
            )
        elif user.user_type in ['provider', 'care_team']:
            return TelehealthRecording.objects.filter(
                Q(session__provider=user) | Q(session__participants__user=user),
                status='completed'
            ).distinct()
        else:
            return TelehealthRecording.objects.none()
    
    @action(detail=True, methods=['get'])
    def download_url(self, request, pk=None):
        """Get download URL for recording"""
        recording = self.get_object()
        
        if recording.status != 'completed':
            return Response(
                {'error': 'Recording is not ready for download'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return download URL (implementation depends on storage backend)
        return Response({
            'download_url': f'/api/telehealth/recordings/{recording.id}/download/',
            'expires_at': recording.expires_at,
            'file_size_mb': recording.file_size_mb
        })


class TelehealthWaitingRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for waiting rooms"""
    
    serializer_class = TelehealthWaitingRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type in ['provider', 'care_team']:
            return TelehealthWaitingRoom.objects.filter(
                session__provider=user
            )
        else:
            return TelehealthWaitingRoom.objects.filter(
                session__patient=user
            )
    
    @action(detail=True, methods=['post'])
    def admit_participant(self, request, pk=None):
        """Admit participant from waiting room"""
        waiting_room = self.get_object()
        participant_id = request.data.get('participant_id')
        
        try:
            from .models import WaitingRoomParticipant
            waiting_participant = WaitingRoomParticipant.objects.get(
                waiting_room=waiting_room,
                participant_id=participant_id,
                admitted_at__isnull=True,
                denied_at__isnull=True
            )
            
            waiting_participant.admitted_at = timezone.now()
            waiting_participant.save()
            
            return Response({'message': 'Participant admitted to session'})
            
        except WaitingRoomParticipant.DoesNotExist:
            return Response(
                {'error': 'Participant not found in waiting room'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def deny_participant(self, request, pk=None):
        """Deny participant from waiting room"""
        waiting_room = self.get_object()
        participant_id = request.data.get('participant_id')
        reason = request.data.get('reason', '')
        
        try:
            from .models import WaitingRoomParticipant
            waiting_participant = WaitingRoomParticipant.objects.get(
                waiting_room=waiting_room,
                participant_id=participant_id,
                admitted_at__isnull=True,
                denied_at__isnull=True
            )
            
            waiting_participant.denied_at = timezone.now()
            waiting_participant.denial_reason = reason
            waiting_participant.save()
            
            return Response({'message': 'Participant denied access'})
            
        except WaitingRoomParticipant.DoesNotExist:
            return Response(
                {'error': 'Participant not found in waiting room'},
                status=status.HTTP_404_NOT_FOUND
            )

def check_admin_or_coordinator_permission(user):
    """Helper function to check if user can modify clinic settings"""
    return user.user_type in ['admin', 'care_team'] and user.is_staff


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_clinic_settings(request):
    """Get current clinic telehealth settings"""
    settings_obj = ClinicSettings.get_current_settings()
    serializer = ClinicSettingsSerializer(settings_obj)
    return Response(serializer.data)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def update_clinic_settings(request):
    """Update clinic telehealth settings (Admin/Coordinator only)"""
    
    # Check permissions
    if not check_admin_or_coordinator_permission(request.user):
        return Response(
            {'error': 'Access denied. Only administrators and coordinators can modify clinic settings.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    settings_obj = ClinicSettings.get_current_settings()
    old_values = {
        'default_telehealth_tier': settings_obj.default_telehealth_tier,
        'enable_fallback_to_webrtc': settings_obj.enable_fallback_to_webrtc,
        'enable_patient_choice': settings_obj.enable_patient_choice,
        'enable_bandwidth_detection': settings_obj.enable_bandwidth_detection,
        'minimum_bandwidth_for_zoom': settings_obj.minimum_bandwidth_for_zoom,
        'enable_high_contrast_mode': settings_obj.enable_high_contrast_mode,
        'default_language': settings_obj.default_language,
    }
    
    serializer = ClinicSettingsSerializer(
        settings_obj, 
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Save the settings
        updated_settings = serializer.save(last_modified_by=request.user)
        
        # Create audit log entry
        new_values = {
            'default_telehealth_tier': updated_settings.default_telehealth_tier,
            'enable_fallback_to_webrtc': updated_settings.enable_fallback_to_webrtc,
            'enable_patient_choice': updated_settings.enable_patient_choice,
            'enable_bandwidth_detection': updated_settings.enable_bandwidth_detection,
            'minimum_bandwidth_for_zoom': updated_settings.minimum_bandwidth_for_zoom,
            'enable_high_contrast_mode': updated_settings.enable_high_contrast_mode,
            'default_language': updated_settings.default_language,
        }
        
        # Determine change type
        change_type = 'tier_change'
        if old_values['default_telehealth_tier'] != new_values['default_telehealth_tier']:
            change_type = 'tier_change'
        elif old_values['enable_fallback_to_webrtc'] != new_values['enable_fallback_to_webrtc']:
            change_type = 'fallback_toggle'
        elif old_values['enable_patient_choice'] != new_values['enable_patient_choice']:
            change_type = 'patient_choice_toggle'
        elif old_values['enable_bandwidth_detection'] != new_values['enable_bandwidth_detection'] or \
             old_values['minimum_bandwidth_for_zoom'] != new_values['minimum_bandwidth_for_zoom']:
            change_type = 'bandwidth_setting'
        elif old_values['enable_high_contrast_mode'] != new_values['enable_high_contrast_mode']:
            change_type = 'accessibility_change'
        elif old_values['default_language'] != new_values['default_language']:
            change_type = 'language_change'
        
        # Create audit log
        TelehealthTierAuditLog.objects.create(
            change_type=change_type,
            user=request.user,
            old_value=old_values,
            new_value=new_values,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            reason=request.data.get('reason', 'Settings updated via web interface')
        )
        
        # Also create general audit log
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            action_description=f'Updated clinic telehealth settings: {change_type}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            resource_type='ClinicSettings',
            resource_id='1'
        )
        
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_telehealth_tier_preview(request):
    """Get preview information for different telehealth tiers"""
    
    webrtc_preview = {
        'tier': 'webrtc',
        'title': 'Free Tier (WebRTC)',
        'description': 'Peer-to-peer video communication for cost-effective telehealth',
        'features': [
            'Peer-to-peer video calls',
            'Audio and video communication', 
            'Text chat during sessions',
            'Basic screen sharing (limited)',
            'Connection quality monitoring'
        ],
        'pros': [
            'No additional cost',
            'Works well with good internet connection',
            'Direct peer-to-peer connection',
            'Lower latency in ideal conditions',
            'Privacy-focused (no server recording)'
        ],
        'cons': [
            'May struggle with poor network conditions',
            'Limited features compared to enterprise solutions',
            'No advanced recording capabilities',
            'Connection quality depends on both endpoints',
            'Limited support for multiple participants'
        ],
        'ideal_for': [
            'Rural clinics with budget constraints',
            'Low-bandwidth environments',
            'Basic consultation needs',
            'Privacy-sensitive sessions',
            'Small practices'
        ],
        'bandwidth_requirement': '512 kbps recommended',
        'cost': 'Free'
    }
    
    zoom_preview = {
        'tier': 'zoom',
        'title': 'Paid Tier (Zoom SDK)',
        'description': 'Enterprise-grade video platform with advanced features',
        'features': [
            'HD video and audio quality',
            'Advanced screen sharing',
            'Session recording and storage',
            'Waiting rooms',
            'Multi-participant support',
            'Chat and file sharing',
            'Virtual backgrounds',
            'Breakout rooms support'
        ],
        'pros': [
            'Enterprise-grade reliability',
            'Advanced features and controls',
            'Better performance in poor network conditions',
            'Professional recording capabilities',
            'Excellent multi-participant support',
            'HIPAA-compliant infrastructure',
            'Advanced security features'
        ],
        'cons': [
            'Additional subscription cost required',
            'Requires stable internet connection',
            'More complex setup and configuration',
            'Data stored on third-party servers',
            'May be overkill for simple consultations'
        ],
        'ideal_for': [
            'Large healthcare organizations',
            'Multi-participant consultations',
            'Training and education sessions',
            'Clinics requiring recording capabilities',
            'Areas with stable high-speed internet'
        ],
        'bandwidth_requirement': '1.5 Mbps recommended',
        'cost': 'Subscription required'
    }
    
    return Response({
        'webrtc': webrtc_preview,
        'zoom': zoom_preview
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_permissions(request):
    """Check current user's permissions for telehealth settings"""
    
    user = request.user
    permissions = {
        'can_view_settings': True,  # All authenticated users can view
        'can_edit_settings': check_admin_or_coordinator_permission(user),
        'can_view_audit_logs': check_admin_or_coordinator_permission(user),
        'can_view_analytics': check_admin_or_coordinator_permission(user),
        'user_type': user.user_type,
        'user_name': user.full_name,
        'subscription_tier': user.subscription_tier,
        'can_use_zoom': user.can_use_zoom
    }
    
    return Response(permissions)
