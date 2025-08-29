from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Patient, Encounter, Medication, LabResult, Appointment
from .serializers import (
    PatientSerializer,
    EncounterSerializer,
    MedicationSerializer,
    LabResultSerializer,
    AppointmentSerializer
)
from .services import OpenEMRService


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for patient management"""
    
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            # Patients can only see their own record
            return Patient.objects.filter(user=user)
        elif user.user_type in ['provider', 'care_team']:
            # Providers can see all patients
            return Patient.objects.all()
        else:
            return Patient.objects.none()
    
    @action(detail=True, methods=['post'])
    def sync_with_openemr(self, request, pk=None):
        """Sync patient data with OpenEMR"""
        patient = self.get_object()
        
        try:
            openemr_service = OpenEMRService()
            updated_patient = openemr_service.sync_patient(patient)
            serializer = self.get_serializer(updated_patient)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Sync failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get patient summary with recent data"""
        patient = self.get_object()
        
        # Get recent encounters
        recent_encounters = patient.encounters.filter(
            start_time__gte=timezone.now() - timedelta(days=90)
        ).order_by('-start_time')[:5]
        
        # Get active medications
        active_medications = patient.medication_list.filter(is_active=True)
        
        # Get recent lab results
        recent_labs = patient.lab_results.filter(
            resulted_datetime__gte=timezone.now() - timedelta(days=90)
        ).order_by('-resulted_datetime')[:10]
        
        # Get upcoming appointments
        upcoming_appointments = patient.appointments.filter(
            start_time__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('start_time')[:5]
        
        return Response({
            'patient': PatientSerializer(patient).data,
            'recent_encounters': EncounterSerializer(recent_encounters, many=True).data,
            'active_medications': MedicationSerializer(active_medications, many=True).data,
            'recent_labs': LabResultSerializer(recent_labs, many=True).data,
            'upcoming_appointments': AppointmentSerializer(upcoming_appointments, many=True).data,
        })


class EncounterViewSet(viewsets.ModelViewSet):
    """ViewSet for encounter management"""
    
    serializer_class = EncounterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            # Patients can only see their own encounters
            return Encounter.objects.filter(patient__user=user)
        elif user.user_type in ['provider', 'care_team']:
            # Providers can see all encounters or filter by patient
            queryset = Encounter.objects.all()
            patient_id = self.request.query_params.get('patient_id')
            if patient_id:
                queryset = queryset.filter(patient_id=patient_id)
            return queryset
        else:
            return Encounter.objects.none()
    
    def perform_create(self, serializer):
        """Set provider when creating encounter"""
        if self.request.user.user_type in ['provider', 'care_team']:
            serializer.save(provider=self.request.user)
        else:
            serializer.save()


class MedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for medication management"""
    
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            return Medication.objects.filter(patient__user=user)
        elif user.user_type in ['provider', 'care_team']:
            queryset = Medication.objects.all()
            patient_id = self.request.query_params.get('patient_id')
            if patient_id:
                queryset = queryset.filter(patient_id=patient_id)
            return queryset
        else:
            return Medication.objects.none()
    
    def perform_create(self, serializer):
        """Set prescriber when creating medication"""
        if self.request.user.user_type == 'provider':
            serializer.save(prescriber=self.request.user)
        else:
            serializer.save()


class LabResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for lab results (read-only)"""
    
    serializer_class = LabResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            return LabResult.objects.filter(patient__user=user)
        elif user.user_type in ['provider', 'care_team']:
            queryset = LabResult.objects.all()
            patient_id = self.request.query_params.get('patient_id')
            if patient_id:
                queryset = queryset.filter(patient_id=patient_id)
            return queryset
        else:
            return LabResult.objects.none()


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for appointment management"""
    
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            return Appointment.objects.filter(patient__user=user)
        elif user.user_type in ['provider', 'care_team']:
            queryset = Appointment.objects.all()
            
            # Filter by provider if specified
            provider_id = self.request.query_params.get('provider_id')
            if provider_id:
                queryset = queryset.filter(provider_id=provider_id)
            
            # Filter by patient if specified
            patient_id = self.request.query_params.get('patient_id')
            if patient_id:
                queryset = queryset.filter(patient_id=patient_id)
            
            # Filter by date range
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            if start_date:
                queryset = queryset.filter(start_time__gte=start_date)
            if end_date:
                queryset = queryset.filter(start_time__lte=end_date)
            
            return queryset
        else:
            return Appointment.objects.none()
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments"""
        today = timezone.now().date()
        appointments = self.get_queryset().filter(
            start_time__date=today
        ).order_by('start_time')
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments"""
        now = timezone.now()
        appointments = self.get_queryset().filter(
            start_time__gte=now,
            status__in=['scheduled', 'confirmed']
        ).order_by('start_time')[:10]
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in patient for appointment"""
        appointment = self.get_object()
        appointment.status = 'arrived'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed"""
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.end_time = timezone.now()
        appointment.save()
        
        # Create encounter if doesn't exist
        if not hasattr(appointment, 'encounter'):
            Encounter.objects.create(
                openemr_encounter_id=f"enc_{appointment.id}_{timezone.now().timestamp()}",
                patient=appointment.patient,
                provider=appointment.provider,
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                encounter_class='VR' if appointment.is_telehealth else 'AMB',
                chief_complaint=appointment.chief_complaint,
                notes=appointment.notes
            )
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)