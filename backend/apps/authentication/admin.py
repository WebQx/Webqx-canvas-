from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, AuditLog


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'subscription_tier', 'is_verified', 'date_joined')
    list_filter = ('user_type', 'subscription_tier', 'is_verified', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Healthcare Info', {
            'fields': ('user_type', 'subscription_tier', 'patient_id', 'provider_id')
        }),
        ('Personal Info', {
            'fields': ('phone_number', 'date_of_birth', 'language_preference', 'timezone')
        }),
        ('Security', {
            'fields': ('biometric_enabled', 'two_factor_enabled', 'is_verified')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'medical_record_number', 'license_number', 'specialty')
    search_fields = ('user__username', 'medical_record_number', 'license_number')
    list_filter = ('specialty',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'timestamp', 'ip_address')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('user__username', 'action_description')
    readonly_fields = ('timestamp',)