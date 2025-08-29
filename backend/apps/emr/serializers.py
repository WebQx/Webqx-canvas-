from rest_framework import serializers
from .models import Patient, Encounter, Medication, LabResult, Appointment


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model"""
    
    full_name = serializers.ReadOnlyField()
    age = serializers.SerializerMethodField()
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'last_sync')
    
    def get_age(self, obj):
        """Calculate patient age"""
        from datetime import date
        if obj.date_of_birth:
            today = date.today()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None


class EncounterSerializer(serializers.ModelSerializer):
    """Serializer for Encounter model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.full_name', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Encounter
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'last_sync')
    
    def get_duration(self, obj):
        """Calculate encounter duration in minutes"""
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return int(delta.total_seconds() / 60)
        return None


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for Medication model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    prescriber_name = serializers.CharField(source='prescriber.full_name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Medication
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_is_expired(self, obj):
        """Check if medication is expired"""
        from datetime import date
        if obj.end_date:
            return obj.end_date < date.today()
        return False


class LabResultSerializer(serializers.ModelSerializer):
    """Serializer for LabResult model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    provider_name = serializers.CharField(source='ordering_provider.full_name', read_only=True)
    is_abnormal = serializers.SerializerMethodField()
    
    class Meta:
        model = LabResult
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_is_abnormal(self, obj):
        """Check if lab result is abnormal"""
        return obj.interpretation in ['H', 'L', 'A', 'C']


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.full_name', read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    can_join_telehealth = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_duration_formatted(self, obj):
        """Format duration in hours and minutes"""
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    def get_is_upcoming(self, obj):
        """Check if appointment is upcoming"""
        from django.utils import timezone
        return obj.start_time > timezone.now()
    
    def get_can_join_telehealth(self, obj):
        """Check if user can join telehealth appointment"""
        from django.utils import timezone
        if not obj.is_telehealth:
            return False
        
        # Allow joining 15 minutes before appointment
        join_time = obj.start_time - timezone.timedelta(minutes=15)
        return timezone.now() >= join_time and obj.status in ['scheduled', 'confirmed', 'arrived']


# Simplified serializers for nested relationships
class PatientBasicSerializer(serializers.ModelSerializer):
    """Basic patient serializer for nested use"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = ('id', 'medical_record_number', 'full_name', 'date_of_birth')


class ProviderBasicSerializer(serializers.ModelSerializer):
    """Basic provider serializer for nested use"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = 'authentication.User'
        fields = ('id', 'username', 'full_name', 'user_type')


class AppointmentBasicSerializer(serializers.ModelSerializer):
    """Basic appointment serializer for calendar views"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = (
            'id', 'patient_name', 'provider_name', 'appointment_type',
            'status', 'start_time', 'end_time', 'duration_minutes',
            'is_telehealth', 'chief_complaint'
        )