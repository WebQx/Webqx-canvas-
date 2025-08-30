from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

# Import clinic-specific models
from .clinic_models import ClinicSettings, TelehealthTierAuditLog, TelehealthUsageAnalytics


class TelehealthSession(models.Model):
    """Telehealth video session model"""
    
    SESSION_STATUS = [
        ('scheduled', 'Scheduled'),
        ('waiting', 'Waiting for participants'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    PLATFORM_TYPES = [
        ('webrtc', 'WebRTC (Free)'),
        ('zoom', 'Zoom SDK (Premium)'),
        ('jitsi', 'Jitsi Meet'),
    ]
    
    # Session Identification
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    room_name = models.CharField(max_length=100, unique=True)
    
    # Participants
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telehealth_sessions_as_patient'
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telehealth_sessions_as_provider'
    )
    
    # Platform Configuration
    platform = models.CharField(max_length=20, choices=PLATFORM_TYPES, default='webrtc')
    
    # Session Details
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='scheduled')
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Platform-specific Data
    zoom_meeting_id = models.CharField(max_length=100, blank=True)
    zoom_meeting_password = models.CharField(max_length=50, blank=True)
    zoom_join_url = models.URLField(blank=True)
    webrtc_room_config = models.JSONField(default=dict, blank=True)
    jitsi_room_url = models.URLField(blank=True)
    
    # Session Notes
    notes = models.TextField(blank=True)
    recording_enabled = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True)
    
    # Technical Details
    connection_quality = models.CharField(max_length=20, blank=True)  # excellent, good, fair, poor
    technical_issues = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_start']
    
    def __str__(self):
        return f"Telehealth Session {self.session_id} - {self.patient.full_name} with {self.provider.full_name}"
    
    @property
    def duration_minutes(self):
        """Calculate session duration in minutes"""
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def can_join(self):
        """Check if session can be joined"""
        now = timezone.now()
        # Allow joining 15 minutes before scheduled start
        join_time = self.scheduled_start - timezone.timedelta(minutes=15)
        return self.status in ['scheduled', 'waiting'] and now >= join_time
    
    @property
    def is_active(self):
        """Check if session is currently active"""
        return self.status == 'active'


class TelehealthParticipant(models.Model):
    """Track participants in telehealth sessions"""
    
    PARTICIPANT_ROLES = [
        ('patient', 'Patient'),
        ('provider', 'Provider'),
        ('observer', 'Observer'),
        ('interpreter', 'Interpreter'),
    ]
    
    session = models.ForeignKey(
        TelehealthSession,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=PARTICIPANT_ROLES)
    
    # Connection Details
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    connection_id = models.CharField(max_length=100, blank=True)
    
    # Permissions
    can_share_screen = models.BooleanField(default=False)
    can_record = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    
    # Technical Stats
    video_enabled = models.BooleanField(default=True)
    audio_enabled = models.BooleanField(default=True)
    connection_quality = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['session', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_role_display()} in {self.session.session_id}"
    
    @property
    def duration_minutes(self):
        """Calculate participant duration in minutes"""
        if self.joined_at and self.left_at:
            delta = self.left_at - self.joined_at
            return int(delta.total_seconds() / 60)
        return None


class WebRTCSignaling(models.Model):
    """WebRTC signaling messages for peer-to-peer connections"""
    
    MESSAGE_TYPES = [
        ('offer', 'Offer'),
        ('answer', 'Answer'),
        ('ice_candidate', 'ICE Candidate'),
        ('bye', 'Bye'),
    ]
    
    session = models.ForeignKey(
        TelehealthSession,
        on_delete=models.CASCADE,
        related_name='signaling_messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_signaling_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_signaling_messages',
        null=True, blank=True  # null for broadcast messages
    )
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    message_data = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type} from {self.sender.username} at {self.created_at}"


class TelehealthDeviceTest(models.Model):
    """Device and connection tests before joining sessions"""
    
    TEST_TYPES = [
        ('microphone', 'Microphone Test'),
        ('camera', 'Camera Test'),
        ('speaker', 'Speaker Test'),
        ('network', 'Network Test'),
        ('bandwidth', 'Bandwidth Test'),
    ]
    
    TEST_RESULTS = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('warning', 'Warning'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tests'
    )
    session = models.ForeignKey(
        TelehealthSession,
        on_delete=models.CASCADE,
        related_name='device_tests',
        null=True, blank=True
    )
    
    test_type = models.CharField(max_length=20, choices=TEST_TYPES)
    test_result = models.CharField(max_length=20, choices=TEST_RESULTS)
    
    # Test Details
    details = models.JSONField(default=dict)  # Store test-specific data
    error_message = models.TextField(blank=True)
    
    # Network metrics
    upload_speed_mbps = models.FloatField(null=True, blank=True)
    download_speed_mbps = models.FloatField(null=True, blank=True)
    latency_ms = models.IntegerField(null=True, blank=True)
    packet_loss_percent = models.FloatField(null=True, blank=True)
    
    tested_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-tested_at']
    
    def __str__(self):
        return f"{self.get_test_type_display()} - {self.get_test_result_display()} for {self.user.username}"


class TelehealthRecording(models.Model):
    """Recording metadata for telehealth sessions"""
    
    RECORDING_STATUS = [
        ('starting', 'Starting'),
        ('recording', 'Recording'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    session = models.OneToOneField(
        TelehealthSession,
        on_delete=models.CASCADE,
        related_name='recording'
    )
    
    # Recording Details
    status = models.CharField(max_length=20, choices=RECORDING_STATUS, default='starting')
    file_path = models.CharField(max_length=500, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Platform-specific
    zoom_recording_id = models.CharField(max_length=100, blank=True)
    zoom_download_url = models.URLField(blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Consent and Privacy
    consent_obtained = models.BooleanField(default=False)
    consent_participants = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recording for {self.session.session_id} - {self.status}"
    
    @property
    def file_size_mb(self):
        """File size in MB"""
        if self.file_size_bytes:
            return round(self.file_size_bytes / (1024 * 1024), 2)
        return None


class TelehealthWaitingRoom(models.Model):
    """Waiting room for telehealth sessions"""
    
    session = models.OneToOneField(
        TelehealthSession,
        on_delete=models.CASCADE,
        related_name='waiting_room'
    )
    
    # Configuration
    is_enabled = models.BooleanField(default=True)
    admission_control = models.BooleanField(default=True)  # Require provider approval
    
    # Participants waiting
    waiting_participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='WaitingRoomParticipant',
        related_name='waiting_rooms'
    )
    
    # Messages
    welcome_message = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Waiting room for {self.session.session_id}"


class WaitingRoomParticipant(models.Model):
    """Participants in waiting room"""
    
    waiting_room = models.ForeignKey(
        TelehealthWaitingRoom,
        on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    # Status
    joined_waiting_at = models.DateTimeField(auto_now_add=True)
    admitted_at = models.DateTimeField(null=True, blank=True)
    denied_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    # Reason for denial
    denial_reason = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['waiting_room', 'participant']
    
    def __str__(self):
        return f"{self.participant.username} in waiting room for {self.waiting_room.session.session_id}"