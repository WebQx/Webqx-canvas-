from django.db import models
from django.conf import settings
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.encounter import Encounter as FHIREncounter
import json


class Patient(models.Model):
    """Patient model with OpenEMR integration"""
    
    # Link to auth user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_record',
        null=True, blank=True
    )
    
    # OpenEMR Integration
    openemr_patient_id = models.CharField(max_length=50, unique=True)
    medical_record_number = models.CharField(max_length=50, unique=True)
    
    # Demographics
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('unknown', 'Unknown')
    ])
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='US')
    
    # Medical Information
    blood_type = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} (MRN: {self.medical_record_number})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_fhir(self):
        """Convert to FHIR Patient resource"""
        return FHIRPatient.parse_obj({
            "resourceType": "Patient",
            "id": str(self.openemr_patient_id),
            "identifier": [{
                "value": self.medical_record_number,
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "MR"
                    }]
                }
            }],
            "name": [{
                "family": self.last_name,
                "given": [self.first_name]
            }],
            "gender": self.gender,
            "birthDate": str(self.date_of_birth),
            "telecom": [
                {"system": "phone", "value": self.phone},
                {"system": "email", "value": self.email}
            ] if self.phone or self.email else [],
            "address": [{
                "line": [self.address_line1, self.address_line2],
                "city": self.city,
                "state": self.state,
                "postalCode": self.zip_code,
                "country": self.country
            }] if self.address_line1 else []
        })


class Encounter(models.Model):
    """Medical encounter/visit model"""
    
    ENCOUNTER_STATUS = [
        ('planned', 'Planned'),
        ('arrived', 'Arrived'),
        ('triaged', 'Triaged'),
        ('in-progress', 'In Progress'),
        ('onleave', 'On Leave'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
    ]
    
    ENCOUNTER_CLASS = [
        ('AMB', 'Ambulatory'),
        ('EMER', 'Emergency'),
        ('IMP', 'Inpatient'),
        ('OBSENC', 'Observation'),
        ('VR', 'Virtual'),
    ]
    
    # OpenEMR Integration
    openemr_encounter_id = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='encounters')
    
    # Encounter Details
    status = models.CharField(max_length=20, choices=ENCOUNTER_STATUS, default='planned')
    encounter_class = models.CharField(max_length=10, choices=ENCOUNTER_CLASS, default='AMB')
    
    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Provider Information
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='encounters_as_provider'
    )
    
    # Clinical Information
    chief_complaint = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-start_time']
        
    def __str__(self):
        return f"Encounter {self.openemr_encounter_id} - {self.patient.full_name} on {self.start_time.date()}"


class Medication(models.Model):
    """Patient medication model"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medication_list')
    
    # Medication Details
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    route = models.CharField(max_length=50, blank=True)
    
    # Prescriber
    prescriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='prescribed_medications'
    )
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Notes
    instructions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        
    def __str__(self):
        return f"{self.name} - {self.dosage} for {self.patient.full_name}"


class LabResult(models.Model):
    """Laboratory test results"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, null=True, blank=True)
    
    # Test Information
    test_name = models.CharField(max_length=200)
    test_code = models.CharField(max_length=50, blank=True)  # LOINC code
    category = models.CharField(max_length=100, blank=True)
    
    # Results
    result_value = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, blank=True)
    reference_range = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='final')
    
    # Interpretation
    interpretation = models.CharField(max_length=20, blank=True, choices=[
        ('H', 'High'),
        ('L', 'Low'),
        ('N', 'Normal'),
        ('A', 'Abnormal'),
        ('C', 'Critical'),
    ])
    
    # Timing
    collected_datetime = models.DateTimeField()
    resulted_datetime = models.DateTimeField()
    
    # Provider
    ordering_provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordered_labs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-resulted_datetime']
        
    def __str__(self):
        return f"{self.test_name}: {self.result_value} {self.unit} for {self.patient.full_name}"


class Appointment(models.Model):
    """Patient appointment model"""
    
    APPOINTMENT_STATUS = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('arrived', 'Arrived'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no-show', 'No Show'),
    ]
    
    APPOINTMENT_TYPE = [
        ('routine', 'Routine Visit'),
        ('follow-up', 'Follow-up'),
        ('urgent', 'Urgent Care'),
        ('telehealth', 'Telehealth'),
        ('consultation', 'Consultation'),
    ]
    
    # OpenEMR Integration
    openemr_appointment_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_provider'
    )
    
    # Appointment Details
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPE, default='routine')
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='scheduled')
    
    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    
    # Details
    chief_complaint = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Telehealth
    is_telehealth = models.BooleanField(default=False)
    meeting_url = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
        
    def __str__(self):
        return f"Appointment: {self.patient.full_name} with {self.provider.full_name} on {self.start_time}"