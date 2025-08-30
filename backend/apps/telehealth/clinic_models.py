from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class ClinicSettings(models.Model):
    """
    Clinic-wide settings for telehealth services.
    Controls the default telehealth tier and related preferences.
    """
    
    TELEHEALTH_TIERS = [
        ('webrtc', 'Free Tier (WebRTC)'),
        ('zoom', 'Paid Tier (Zoom SDK)'),
    ]
    
    # Clinic identification - for now, we'll have one global setting
    # In the future, this could be linked to a Clinic model
    clinic_name = models.CharField(max_length=200, default='Default Clinic')
    
    # Primary telehealth tier setting
    default_telehealth_tier = models.CharField(
        max_length=20, 
        choices=TELEHEALTH_TIERS, 
        default='webrtc',
        help_text="Default telehealth platform for new sessions"
    )
    
    # Fallback and advanced options
    enable_fallback_to_webrtc = models.BooleanField(
        default=True,
        help_text="Automatically fallback to WebRTC if Zoom SDK fails"
    )
    
    enable_patient_choice = models.BooleanField(
        default=True,
        help_text="Allow patients to choose their preferred tier at session start"
    )
    
    # Bandwidth and quality settings
    enable_bandwidth_detection = models.BooleanField(
        default=True,
        help_text="Automatically detect bandwidth and suggest appropriate tier"
    )
    
    minimum_bandwidth_for_zoom = models.IntegerField(
        default=1024,  # 1 Mbps in kbps
        help_text="Minimum bandwidth in kbps required to suggest Zoom"
    )
    
    # Accessibility settings
    enable_high_contrast_mode = models.BooleanField(
        default=False,
        help_text="Enable high contrast mode for better accessibility"
    )
    
    default_language = models.CharField(
        max_length=10,
        default='en',
        choices=[
            ('en', 'English'),
            ('es', 'Spanish'),
            ('ur', 'Urdu'),
            ('ar', 'Arabic'),
            ('fr', 'French'),
        ],
        help_text="Default language for telehealth interface"
    )
    
    # Audit and compliance
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clinic_settings_modifications'
    )
    
    class Meta:
        verbose_name = "Clinic Settings"
        verbose_name_plural = "Clinic Settings"
    
    def __str__(self):
        return f"{self.clinic_name} - {self.get_default_telehealth_tier_display()}"
    
    def clean(self):
        """Validate settings based on business rules"""
        if self.default_telehealth_tier == 'zoom' and not self.enable_fallback_to_webrtc:
            # This is allowed but might be risky
            pass
        
        if self.minimum_bandwidth_for_zoom < 500:
            raise ValidationError("Minimum bandwidth for Zoom should be at least 500 kbps")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_current_settings(cls):
        """Get the current clinic settings, creating default if none exist"""
        settings_obj, created = cls.objects.get_or_create(
            pk=1,  # Single settings instance for now
            defaults={
                'clinic_name': 'Default Clinic',
                'default_telehealth_tier': 'webrtc'
            }
        )
        return settings_obj


class TelehealthTierAuditLog(models.Model):
    """
    Audit log specifically for telehealth tier changes.
    Required for compliance tracking.
    """
    
    CHANGE_TYPES = [
        ('tier_change', 'Telehealth Tier Changed'),
        ('fallback_toggle', 'Fallback Setting Changed'),
        ('patient_choice_toggle', 'Patient Choice Setting Changed'),
        ('bandwidth_setting', 'Bandwidth Setting Changed'),
        ('accessibility_change', 'Accessibility Setting Changed'),
        ('language_change', 'Language Setting Changed'),
    ]
    
    # What changed
    change_type = models.CharField(max_length=30, choices=CHANGE_TYPES)
    
    # Who made the change
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telehealth_audit_logs'
    )
    
    # When it happened
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Change details
    old_value = models.JSONField(default=dict, help_text="Previous setting values")
    new_value = models.JSONField(default=dict, help_text="New setting values")
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    reason = models.TextField(blank=True, help_text="Reason for the change")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Telehealth Tier Audit Log"
        verbose_name_plural = "Telehealth Tier Audit Logs"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_change_type_display()} at {self.timestamp}"


class TelehealthUsageAnalytics(models.Model):
    """
    Track usage patterns to provide recommendations for optimal tier selection.
    """
    
    # Time period
    date = models.DateField()
    
    # Usage metrics
    webrtc_sessions_count = models.IntegerField(default=0)
    zoom_sessions_count = models.IntegerField(default=0)
    
    webrtc_total_duration_minutes = models.IntegerField(default=0)
    zoom_total_duration_minutes = models.IntegerField(default=0)
    
    # Quality metrics
    webrtc_average_quality_score = models.FloatField(default=0.0)  # 0-10 scale
    zoom_average_quality_score = models.FloatField(default=0.0)
    
    webrtc_connection_failures = models.IntegerField(default=0)
    zoom_connection_failures = models.IntegerField(default=0)
    
    # Patient feedback (if available)
    webrtc_satisfaction_score = models.FloatField(default=0.0)  # 0-5 scale
    zoom_satisfaction_score = models.FloatField(default=0.0)
    
    # Calculated fields
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
        verbose_name = "Telehealth Usage Analytics"
        verbose_name_plural = "Telehealth Usage Analytics"
    
    def __str__(self):
        return f"Analytics for {self.date} - WebRTC: {self.webrtc_sessions_count}, Zoom: {self.zoom_sessions_count}"
    
    @property
    def total_sessions(self):
        return self.webrtc_sessions_count + self.zoom_sessions_count
    
    @property
    def webrtc_usage_percentage(self):
        if self.total_sessions == 0:
            return 0
        return (self.webrtc_sessions_count / self.total_sessions) * 100
    
    @property
    def zoom_usage_percentage(self):
        if self.total_sessions == 0:
            return 0
        return (self.zoom_sessions_count / self.total_sessions) * 100
    
    def get_tier_recommendation(self):
        """
        Provide AI-powered recommendation based on usage patterns.
        Simple rule-based logic for now.
        """
        if self.total_sessions < 10:
            return {
                'recommended_tier': 'webrtc',
                'reason': 'Low session volume - WebRTC is cost-effective',
                'confidence': 0.7
            }
        
        if self.webrtc_connection_failures / max(self.webrtc_sessions_count, 1) > 0.2:
            return {
                'recommended_tier': 'zoom',
                'reason': 'High WebRTC failure rate - Zoom SDK may be more reliable',
                'confidence': 0.8
            }
        
        if self.webrtc_usage_percentage > 80 and self.webrtc_average_quality_score > 7:
            return {
                'recommended_tier': 'webrtc',
                'reason': 'High WebRTC usage with good quality - continue with free tier',
                'confidence': 0.9
            }
        
        return {
            'recommended_tier': 'webrtc',
            'reason': 'Default recommendation - start with free tier',
            'confidence': 0.6
        }