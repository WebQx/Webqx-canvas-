from django.contrib import admin
from .models import (
    TelehealthSession, TelehealthParticipant, WebRTCSignaling,
    TelehealthDeviceTest, TelehealthRecording, TelehealthWaitingRoom
)


@admin.register(TelehealthSession)
class TelehealthSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'patient', 'provider', 'platform', 'status', 'scheduled_start', 'duration_minutes')
    list_filter = ('platform', 'status', 'scheduled_start', 'recording_enabled')
    search_fields = ('session_id', 'patient__username', 'provider__username', 'room_name')
    readonly_fields = ('session_id', 'room_name', 'actual_start', 'actual_end', 'created_at', 'updated_at')


@admin.register(TelehealthParticipant)
class TelehealthParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'role', 'joined_at', 'left_at', 'connection_quality')
    list_filter = ('role', 'is_moderator', 'video_enabled', 'audio_enabled')
    search_fields = ('user__username', 'session__session_id')


@admin.register(TelehealthDeviceTest)
class TelehealthDeviceTestAdmin(admin.ModelAdmin):
    list_display = ('user', 'test_type', 'test_result', 'upload_speed_mbps', 'download_speed_mbps', 'tested_at')
    list_filter = ('test_type', 'test_result', 'tested_at')
    search_fields = ('user__username',)


@admin.register(TelehealthRecording)
class TelehealthRecordingAdmin(admin.ModelAdmin):
    list_display = ('session', 'status', 'duration_seconds', 'file_size_mb', 'consent_obtained', 'expires_at')
    list_filter = ('status', 'consent_obtained', 'started_at')
    search_fields = ('session__session_id',)
    readonly_fields = ('file_size_bytes', 'started_at', 'completed_at', 'created_at')