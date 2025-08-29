from django.contrib import admin
from .models import Patient, Encounter, Medication, LabResult, Appointment


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('medical_record_number', 'full_name', 'date_of_birth', 'gender', 'is_active')
    list_filter = ('gender', 'is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'medical_record_number', 'email')
    readonly_fields = ('created_at', 'updated_at', 'last_sync')


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ('openemr_encounter_id', 'patient', 'provider', 'start_time', 'status')
    list_filter = ('status', 'encounter_class', 'start_time')
    search_fields = ('patient__first_name', 'patient__last_name', 'provider__username')
    readonly_fields = ('created_at', 'updated_at', 'last_sync')


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient', 'dosage', 'frequency', 'is_active', 'start_date')
    list_filter = ('is_active', 'start_date')
    search_fields = ('name', 'patient__first_name', 'patient__last_name')


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'patient', 'result_value', 'unit', 'interpretation', 'resulted_datetime')
    list_filter = ('interpretation', 'status', 'resulted_datetime')
    search_fields = ('test_name', 'patient__first_name', 'patient__last_name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'provider', 'start_time', 'appointment_type', 'status', 'is_telehealth')
    list_filter = ('appointment_type', 'status', 'is_telehealth', 'start_time')
    search_fields = ('patient__first_name', 'patient__last_name', 'provider__username')