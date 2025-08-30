from rest_framework import serializers
from .models import (
    JournalEntry, JournalTag, JournalEntryTag, JournalPrompt,
    JournalPromptResponse, MoodTracking, SymptomLog, JournalExport
)


class JournalTagSerializer(serializers.ModelSerializer):
    """Serializer for journal tags"""
    
    class Meta:
        model = JournalTag
        fields = '__all__'
        read_only_fields = ('created_at',)


class JournalEntryTagSerializer(serializers.ModelSerializer):
    """Serializer for journal entry tags"""
    
    tag = JournalTagSerializer(read_only=True)
    tag_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = JournalEntryTag
        fields = '__all__'
        read_only_fields = ('created_at',)


class JournalEntrySerializer(serializers.ModelSerializer):
    """Serializer for journal entries"""
    
    tags = JournalEntryTagSerializer(
        source='journalentrytag_set',
        many=True,
        read_only=True
    )
    word_count = serializers.ReadOnlyField()
    has_clinical_concerns = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = JournalEntry
        fields = '__all__'
        read_only_fields = (
            'user', 'created_at', 'updated_at', 'sentiment_score',
            'sentiment_label', 'keywords', 'entities', 'topics',
            'urgency_score', 'clinical_flags', 'transcription'
        )
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JournalEntryCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating journal entries"""
    
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = JournalEntry
        fields = (
            'title', 'content', 'entry_type', 'audio_file',
            'mood_rating', 'pain_level', 'is_private',
            'shared_with_provider', 'tag_ids'
        )
    
    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        validated_data['user'] = self.context['request'].user
        
        entry = super().create(validated_data)
        
        # Add tags
        for tag_id in tag_ids:
            try:
                tag = JournalTag.objects.get(id=tag_id)
                JournalEntryTag.objects.create(entry=entry, tag=tag)
            except JournalTag.DoesNotExist:
                pass
        
        return entry


class MoodTrackingSerializer(serializers.ModelSerializer):
    """Serializer for mood tracking"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = MoodTracking
        fields = '__all__'
        read_only_fields = ('user', 'recorded_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SymptomLogSerializer(serializers.ModelSerializer):
    """Serializer for symptom logging"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = SymptomLog
        fields = '__all__'
        read_only_fields = ('user', 'recorded_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JournalPromptSerializer(serializers.ModelSerializer):
    """Serializer for journal prompts"""
    
    prompt_type_display = serializers.CharField(source='get_prompt_type_display', read_only=True)
    
    class Meta:
        model = JournalPrompt
        fields = '__all__'
        read_only_fields = ('created_at',)


class JournalPromptResponseSerializer(serializers.ModelSerializer):
    """Serializer for journal prompt responses"""
    
    prompt = JournalPromptSerializer(read_only=True)
    prompt_id = serializers.IntegerField(write_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = JournalPromptResponse
        fields = '__all__'
        read_only_fields = ('user', 'completed_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JournalExportSerializer(serializers.ModelSerializer):
    """Serializer for journal exports"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    export_format_display = serializers.CharField(source='get_export_format_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalExport
        fields = '__all__'
        read_only_fields = (
            'user', 'file_path', 'file_size_bytes', 'is_complete',
            'error_message', 'created_at', 'expires_at'
        )
    
    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        if obj.file_size_bytes:
            return round(obj.file_size_bytes / (1024 * 1024), 2)
        return None
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JournalInsightsSerializer(serializers.Serializer):
    """Serializer for journal insights and analytics"""
    
    total_entries = serializers.IntegerField()
    avg_sentiment = serializers.FloatField()
    mood_trend = serializers.ListField()
    common_topics = serializers.ListField()
    word_count_trend = serializers.ListField()
    clinical_concerns = serializers.IntegerField()
    
    # Additional computed fields
    entries_this_week = serializers.IntegerField(required=False)
    entries_this_month = serializers.IntegerField(required=False)
    longest_streak = serializers.IntegerField(required=False)
    current_streak = serializers.IntegerField(required=False)


class MoodTrendSerializer(serializers.Serializer):
    """Serializer for mood trend data"""
    
    date = serializers.DateField()
    overall_mood = serializers.IntegerField()
    energy_level = serializers.IntegerField()
    anxiety_level = serializers.IntegerField()
    sleep_quality = serializers.IntegerField(allow_null=True)
    entry_count = serializers.IntegerField(default=1)


class SymptomTrendSerializer(serializers.Serializer):
    """Serializer for symptom trend data"""
    
    date = serializers.DateField()
    symptom_name = serializers.CharField()
    avg_severity = serializers.FloatField()
    frequency = serializers.IntegerField()
    duration_hours = serializers.FloatField(allow_null=True)


class JournalStatsSerializer(serializers.Serializer):
    """Serializer for journal statistics"""
    
    # Basic stats
    total_entries = serializers.IntegerField()
    total_words = serializers.IntegerField()
    avg_words_per_entry = serializers.FloatField()
    
    # Time-based stats
    entries_today = serializers.IntegerField()
    entries_this_week = serializers.IntegerField()
    entries_this_month = serializers.IntegerField()
    
    # Streaks
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    
    # Content analysis
    most_used_tags = serializers.ListField()
    common_keywords = serializers.ListField()
    sentiment_distribution = serializers.DictField()
    
    # Health tracking
    mood_entries = serializers.IntegerField()
    symptom_entries = serializers.IntegerField()
    clinical_flags = serializers.IntegerField()