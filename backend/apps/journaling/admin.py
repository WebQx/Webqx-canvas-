from django.contrib import admin
from .models import (
    JournalEntry, JournalTag, JournalEntryTag, JournalPrompt,
    JournalPromptResponse, MoodTracking, SymptomLog, JournalExport
)


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'entry_type', 'mood_rating', 'sentiment_label', 'created_at', 'has_clinical_concerns')
    list_filter = ('entry_type', 'sentiment_label', 'is_private', 'shared_with_provider', 'created_at')
    search_fields = ('user__username', 'title', 'content')
    readonly_fields = ('sentiment_score', 'sentiment_label', 'keywords', 'entities', 'topics', 'urgency_score', 'clinical_flags')


@admin.register(JournalTag)
class JournalTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_system_tag', 'created_by', 'created_at')
    list_filter = ('is_system_tag', 'created_at')
    search_fields = ('name', 'description')


@admin.register(MoodTracking)
class MoodTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'overall_mood', 'energy_level', 'anxiety_level', 'sleep_quality', 'recorded_at')
    list_filter = ('overall_mood', 'energy_level', 'anxiety_level', 'recorded_at')
    search_fields = ('user__username', 'notes')


@admin.register(SymptomLog)
class SymptomLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'symptom_name', 'severity', 'duration_hours', 'recorded_at')
    list_filter = ('severity', 'recorded_at')
    search_fields = ('user__username', 'symptom_name', 'description')


@admin.register(JournalPrompt)
class JournalPromptAdmin(admin.ModelAdmin):
    list_display = ('title', 'prompt_type', 'is_active', 'frequency_days', 'created_at')
    list_filter = ('prompt_type', 'is_active', 'created_at')
    search_fields = ('title', 'question')


@admin.register(JournalExport)
class JournalExportAdmin(admin.ModelAdmin):
    list_display = ('user', 'export_format', 'is_complete', 'created_at', 'expires_at')
    list_filter = ('export_format', 'is_complete', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('file_size_bytes', 'is_complete', 'error_message')