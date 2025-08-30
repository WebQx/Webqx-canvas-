from rest_framework import serializers
from .models import (
    TelehealthSession, TelehealthParticipant, WebRTCSignaling,
    TelehealthDeviceTest, TelehealthRecording, TelehealthWaitingRoom
)
from .clinic_models import ClinicSettings, TelehealthTierAuditLog, TelehealthUsageAnalytics


class TelehealthSessionSerializer(serializers.ModelSerializer):
    """Serializer for telehealth sessions"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.full_name', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    can_join = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TelehealthSession
        fields = '__all__'
        read_only_fields = (
            'session_id', 'room_name', 'actual_start', 'actual_end',
            'zoom_meeting_id', 'zoom_meeting_password', 'zoom_join_url',
            'webrtc_room_config', 'jitsi_room_url', 'created_at', 'updated_at'
        )


class TelehealthParticipantSerializer(serializers.ModelSerializer):
    """Serializer for telehealth participants"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = TelehealthParticipant
        fields = '__all__'
        read_only_fields = ('joined_at', 'left_at', 'connection_id', 'created_at')


class WebRTCSignalingSerializer(serializers.ModelSerializer):
    """Serializer for WebRTC signaling messages"""
    
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.full_name', read_only=True)
    
    class Meta:
        model = WebRTCSignaling
        fields = '__all__'
        read_only_fields = ('created_at', 'processed')


class TelehealthDeviceTestSerializer(serializers.ModelSerializer):
    """Serializer for device tests"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    test_result_display = serializers.CharField(source='get_test_result_display', read_only=True)
    
    class Meta:
        model = TelehealthDeviceTest
        fields = '__all__'
        read_only_fields = ('user', 'tested_at')


class TelehealthRecordingSerializer(serializers.ModelSerializer):
    """Serializer for session recordings"""
    
    file_size_mb = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TelehealthRecording
        fields = '__all__'
        read_only_fields = (
            'file_path', 'file_size_bytes', 'duration_seconds',
            'zoom_recording_id', 'zoom_download_url', 'started_at',
            'completed_at', 'expires_at', 'created_at'
        )


class SessionJoinInfoSerializer(serializers.Serializer):
    """Serializer for session join information"""
    
    platform = serializers.CharField()
    join_url = serializers.URLField(required=False)
    room_id = serializers.CharField(required=False)
    meeting_id = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    ice_servers = serializers.ListField(required=False)
    user_id = serializers.CharField()
    display_name = serializers.CharField()
    role = serializers.CharField()
    permissions = serializers.DictField(required=False)
    connection_id = serializers.CharField()


class TelehealthWaitingRoomSerializer(serializers.ModelSerializer):
    """Serializer for waiting rooms"""
    
    waiting_participants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TelehealthWaitingRoom
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def get_waiting_participants_count(self, obj):
        return obj.waitingroomparticipant_set.filter(
            admitted_at__isnull=True,
            denied_at__isnull=True,
            left_at__isnull=True
        ).count()


class ClinicSettingsSerializer(serializers.ModelSerializer):
    """Serializer for clinic telehealth settings"""
    
    default_telehealth_tier_display = serializers.CharField(
        source='get_default_telehealth_tier_display', 
        read_only=True
    )
    last_modified_by_name = serializers.CharField(
        source='last_modified_by.full_name', 
        read_only=True
    )
    
    class Meta:
        model = ClinicSettings
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'last_modified_by')
    
    def validate_default_telehealth_tier(self, value):
        """Validate that the clinic can use the selected tier"""
        request = self.context.get('request')
        if value == 'zoom' and request and request.user:
            # Check if the clinic/user has zoom access
            # For now, we'll allow it but could add more complex logic
            pass
        return value


class TelehealthTierAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for telehealth tier audit logs"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    
    class Meta:
        model = TelehealthTierAuditLog
        fields = '__all__'
        read_only_fields = ('user', 'timestamp')


class TelehealthUsageAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for telehealth usage analytics"""
    
    total_sessions = serializers.ReadOnlyField()
    webrtc_usage_percentage = serializers.ReadOnlyField()
    zoom_usage_percentage = serializers.ReadOnlyField()
    tier_recommendation = serializers.SerializerMethodField()
    
    class Meta:
        model = TelehealthUsageAnalytics
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def get_tier_recommendation(self, obj):
        return obj.get_tier_recommendation()


class TelehealthTierPreviewSerializer(serializers.Serializer):
    """Serializer for tier preview information"""
    
    tier = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    features = serializers.ListField(child=serializers.CharField())
    pros = serializers.ListField(child=serializers.CharField())
    cons = serializers.ListField(child=serializers.CharField())
    ideal_for = serializers.ListField(child=serializers.CharField())
    bandwidth_requirement = serializers.CharField()
    cost = serializers.CharField()