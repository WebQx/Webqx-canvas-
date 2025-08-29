from django.db import models
from django.conf import settings
from django.utils import timezone


class Message(models.Model):
    """Secure messaging between patients and care team"""
    
    MESSAGE_TYPES = [
        ('general', 'General Message'),
        ('appointment', 'Appointment Related'),
        ('prescription', 'Prescription Request'),
        ('lab_result', 'Lab Result'),
        ('urgent', 'Urgent Message'),
        ('system', 'System Message'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Message Identification
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    
    # Message Content
    subject = models.CharField(max_length=200)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='general')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal')
    
    # Thread Management
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='replies'
    )
    thread_id = models.CharField(max_length=100, db_index=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Related Records
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_messages',
        null=True, blank=True,
        help_text="Patient this message thread is about"
    )
    appointment = models.ForeignKey(
        'emr.Appointment',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    # System fields
    is_system_message = models.BooleanField(default=False)
    auto_delete_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['thread_id', '-sent_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['sender', '-sent_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}: {self.subject}"
    
    def save(self, *args, **kwargs):
        # Generate thread ID if not set
        if not self.thread_id:
            if self.parent_message:
                self.thread_id = self.parent_message.thread_id
            else:
                import uuid
                self.thread_id = str(uuid.uuid4())
        
        super().save(*args, **kwargs)
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class MessageAttachment(models.Model):
    """File attachments for messages"""
    
    ATTACHMENT_TYPES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('lab_result', 'Lab Result'),
        ('prescription', 'Prescription'),
        ('other', 'Other'),
    ]
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    
    # File Details
    file = models.FileField(upload_to='message_attachments/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # Size in bytes
    mime_type = models.CharField(max_length=100)
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, default='document')
    
    # Security
    is_encrypted = models.BooleanField(default=True)
    encryption_key_id = models.CharField(max_length=100, blank=True)
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    downloaded_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Attachment: {self.original_filename} for message {self.message.id}"
    
    @property
    def file_size_mb(self):
        """File size in MB"""
        return round(self.file_size / (1024 * 1024), 2)


class MessageTemplate(models.Model):
    """Pre-defined message templates for common scenarios"""
    
    TEMPLATE_CATEGORIES = [
        ('appointment', 'Appointment'),
        ('prescription', 'Prescription'),
        ('lab_result', 'Lab Result'),
        ('follow_up', 'Follow-up'),
        ('general', 'General'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TEMPLATE_CATEGORIES)
    subject_template = models.CharField(max_length=200)
    content_template = models.TextField()
    
    # Targeting
    user_types = models.JSONField(default=list)  # Which user types can use this template
    
    # Variables that can be used in templates
    available_variables = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.name}"
    
    def render(self, variables=None):
        """Render template with provided variables"""
        if variables is None:
            variables = {}
        
        try:
            subject = self.subject_template.format(**variables)
            content = self.content_template.format(**variables)
            return {
                'subject': subject,
                'content': content
            }
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")


class MessageNotification(models.Model):
    """Notification settings for messages"""
    
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_notification_settings'
    )
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    
    # Priority-based settings
    urgent_immediate = models.BooleanField(default=True)
    high_within_hour = models.BooleanField(default=True)
    normal_daily_digest = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_start_time = models.TimeField(null=True, blank=True)
    quiet_end_time = models.TimeField(null=True, blank=True)
    
    # Auto-reply
    auto_reply_enabled = models.BooleanField(default=False)
    auto_reply_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Message notifications for {self.user.username}"


class MessageRead(models.Model):
    """Track message read status for group messages"""
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_by'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
        ordering = ['read_at']
    
    def __str__(self):
        return f"{self.user.username} read message {self.message.id} at {self.read_at}"


class MessageThreadParticipant(models.Model):
    """Participants in message threads (for group conversations)"""
    
    PARTICIPANT_ROLES = [
        ('participant', 'Participant'),
        ('moderator', 'Moderator'),
        ('observer', 'Observer'),
    ]
    
    thread_id = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=PARTICIPANT_ROLES, default='participant')
    
    # Permissions
    can_send_messages = models.BooleanField(default=True)
    can_add_participants = models.BooleanField(default=False)
    can_remove_participants = models.BooleanField(default=False)
    
    # Status
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Notifications
    notifications_enabled = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['thread_id', 'user']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.username} in thread {self.thread_id}"


class MessageDraft(models.Model):
    """Draft messages that can be saved and resumed later"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_drafts'
    )
    
    # Draft Content
    recipient_id = models.IntegerField(null=True, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    message_type = models.CharField(max_length=20, choices=Message.MESSAGE_TYPES, default='general')
    priority = models.CharField(max_length=10, choices=Message.PRIORITY_LEVELS, default='normal')
    
    # Thread reference
    parent_message_id = models.IntegerField(null=True, blank=True)
    thread_id = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auto_save_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Draft by {self.user.username}: {self.subject[:50]}"