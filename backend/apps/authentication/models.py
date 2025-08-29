from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Extended User model with healthcare-specific fields"""
    
    USER_TYPES = (
        ('patient', 'Patient'),
        ('provider', 'Healthcare Provider'),
        ('admin', 'Administrator'),
        ('care_team', 'Care Team Member'),
    )
    
    SUBSCRIPTION_TIERS = (
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='patient')
    subscription_tier = models.CharField(max_length=20, choices=SUBSCRIPTION_TIERS, default='free')
    
    # Personal Information
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Healthcare Information
    patient_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    provider_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Preferences
    language_preference = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Security
    biometric_enabled = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Status
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_user'
        
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def can_use_zoom(self):
        """Check if user tier allows Zoom integration"""
        return self.subscription_tier in ['premium', 'enterprise']


class UserProfile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Medical Information (for patients)
    medical_record_number = models.CharField(max_length=50, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    
    # Professional Information (for providers)
    license_number = models.CharField(max_length=50, blank=True)
    specialty = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    
    # Avatar and preferences
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"


class AuditLog(models.Model):
    """Audit log for compliance and security tracking"""
    
    ACTION_TYPES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('data_access', 'Data Access'),
        ('data_modify', 'Data Modification'),
        ('export', 'Data Export'),
        ('admin_action', 'Administrative Action'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional context
    resource_type = models.CharField(max_length=50, blank=True)
    resource_id = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} at {self.timestamp}"