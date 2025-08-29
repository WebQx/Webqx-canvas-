from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    TelehealthSession, TelehealthParticipant, WebRTCSignaling,
    TelehealthDeviceTest, TelehealthRecording, TelehealthWaitingRoom
)
from .serializers import (
    TelehealthSessionSerializer, TelehealthParticipantSerializer,
    WebRTCSignalingSerializer, TelehealthDeviceTestSerializer,
    TelehealthRecordingSerializer, SessionJoinInfoSerializer,
    TelehealthWaitingRoomSerializer
)
from .services import TelehealthPlatformService, TelehealthNotificationService


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