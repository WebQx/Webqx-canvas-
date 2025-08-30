from django.db import models
from django.conf import settings
import json


class JournalEntry(models.Model):
    """Patient journal entry with NLP analysis"""
    
    ENTRY_TYPES = [
        ('text', 'Text Entry'),
        ('audio', 'Audio Entry'),
        ('voice_note', 'Voice Note'),
        ('mood', 'Mood Entry'),
        ('symptom', 'Symptom Log'),
    ]
    
    MOOD_LEVELS = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Fair'),
        (4, 'Good'),
        (5, 'Very Good'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journal_entries'
    )
    
    # Entry Content
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='text')
    
    # Audio/Media
    audio_file = models.FileField(upload_to='journal/audio/', null=True, blank=True)
    transcription = models.TextField(blank=True)
    
    # Mood and Symptoms
    mood_rating = models.IntegerField(choices=MOOD_LEVELS, null=True, blank=True)
    pain_level = models.IntegerField(null=True, blank=True, help_text="0-10 scale")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Privacy
    is_private = models.BooleanField(default=True)
    shared_with_provider = models.BooleanField(default=False)
    
    # NLP Analysis Results
    sentiment_score = models.FloatField(null=True, blank=True)  # -1 to 1
    sentiment_label = models.CharField(max_length=20, blank=True)  # positive, negative, neutral
    keywords = models.JSONField(default=list, blank=True)
    entities = models.JSONField(default=list, blank=True)
    topics = models.JSONField(default=list, blank=True)
    
    # Clinical Relevance
    urgency_score = models.FloatField(null=True, blank=True)  # 0 to 1
    clinical_flags = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Journal Entries'
    
    def __str__(self):
        return f"{self.user.username} - {self.title or 'Entry'} ({self.created_at.date()})"
    
    @property
    def word_count(self):
        """Calculate word count of content"""
        return len(self.content.split()) if self.content else 0
    
    @property
    def has_clinical_concerns(self):
        """Check if entry has clinical flags"""
        return bool(self.clinical_flags) or (self.urgency_score and self.urgency_score > 0.7)


class JournalTag(models.Model):
    """Tags for categorizing journal entries"""
    
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    description = models.TextField(blank=True)
    
    # System vs User tags
    is_system_tag = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class JournalEntryTag(models.Model):
    """Many-to-many relationship for journal entry tags"""
    
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    tag = models.ForeignKey(JournalTag, on_delete=models.CASCADE)
    confidence = models.FloatField(default=1.0)  # AI confidence for system tags
    added_by_ai = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['entry', 'tag']


class JournalPrompt(models.Model):
    """System prompts to encourage journaling"""
    
    PROMPT_TYPES = [
        ('daily', 'Daily Check-in'),
        ('mood', 'Mood Tracking'),
        ('symptom', 'Symptom Monitoring'),
        ('gratitude', 'Gratitude Practice'),
        ('reflection', 'Weekly Reflection'),
        ('goal', 'Goal Setting'),
    ]
    
    title = models.CharField(max_length=200)
    question = models.TextField()
    prompt_type = models.CharField(max_length=20, choices=PROMPT_TYPES)
    
    # Targeting
    target_user_types = models.JSONField(default=list)  # ['patient', 'provider']
    target_conditions = models.JSONField(default=list)  # Medical conditions
    
    # Scheduling
    is_active = models.BooleanField(default=True)
    frequency_days = models.IntegerField(default=1)  # How often to show
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['prompt_type', 'title']
    
    def __str__(self):
        return f"{self.get_prompt_type_display()}: {self.title}"


class JournalPromptResponse(models.Model):
    """User responses to journal prompts"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prompt_responses'
    )
    prompt = models.ForeignKey(JournalPrompt, on_delete=models.CASCADE)
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    
    # Response
    response_text = models.TextField()
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'prompt', 'completed_at']


class MoodTracking(models.Model):
    """Dedicated mood tracking with patterns"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mood_entries'
    )
    
    # Mood Metrics
    overall_mood = models.IntegerField(choices=JournalEntry.MOOD_LEVELS)
    energy_level = models.IntegerField(choices=JournalEntry.MOOD_LEVELS)
    anxiety_level = models.IntegerField(choices=JournalEntry.MOOD_LEVELS)
    sleep_quality = models.IntegerField(choices=JournalEntry.MOOD_LEVELS, null=True, blank=True)
    
    # Context
    activities = models.JSONField(default=list)  # What they did
    triggers = models.JSONField(default=list)   # What affected mood
    location = models.CharField(max_length=100, blank=True)
    weather = models.CharField(max_length=50, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Linked Entry
    journal_entry = models.OneToOneField(
        JournalEntry,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        verbose_name_plural = 'Mood Tracking Entries'
    
    def __str__(self):
        return f"{self.user.username} - Mood {self.overall_mood}/5 on {self.recorded_at.date()}"


class SymptomLog(models.Model):
    """Symptom tracking and monitoring"""
    
    SEVERITY_LEVELS = [
        (1, 'Mild'),
        (2, 'Mild-Moderate'),
        (3, 'Moderate'),
        (4, 'Moderate-Severe'),
        (5, 'Severe'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='symptom_logs'
    )
    
    # Symptom Details
    symptom_name = models.CharField(max_length=100)
    severity = models.IntegerField(choices=SEVERITY_LEVELS)
    duration_hours = models.FloatField(null=True, blank=True)
    
    # Context
    triggers = models.JSONField(default=list)
    relief_methods = models.JSONField(default=list)
    medications_taken = models.JSONField(default=list)
    
    # Description
    description = models.TextField(blank=True)
    
    # Linked Entry
    journal_entry = models.OneToOneField(
        JournalEntry,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.symptom_name} (Severity: {self.severity}/5)"


class JournalExport(models.Model):
    """Track journal exports for patients"""
    
    EXPORT_FORMATS = [
        ('pdf', 'PDF Document'),
        ('docx', 'Word Document'),
        ('csv', 'CSV Data'),
        ('json', 'JSON Data'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journal_exports'
    )
    
    # Export Details
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMATS)
    date_range_start = models.DateField()
    date_range_end = models.DateField()
    
    # Filters
    include_private = models.BooleanField(default=True)
    entry_types = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    
    # File
    file_path = models.CharField(max_length=500)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    
    # Status
    is_complete = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Auto-delete after X days
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Export for {self.user.username} ({self.export_format}) - {self.created_at.date()}"