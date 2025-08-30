import requests
import json
from django.conf import settings
from django.utils import timezone
from .models import Patient, Encounter, LabResult, Medication, Appointment
import logging

logger = logging.getLogger(__name__)


class OpenEMRService:
    """Service for OpenEMR integration using FHIR API"""
    
    def __init__(self):
        self.base_url = settings.OPENEMR_BASE_URL
        self.api_token = settings.OPENEMR_API_TOKEN
        self.client_id = settings.OPENEMR_CLIENT_ID
        self.client_secret = settings.OPENEMR_CLIENT_SECRET
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
    
    def authenticate(self):
        """Authenticate with OpenEMR API"""
        try:
            auth_url = f"{self.base_url}/oauth2/default/registration"
            auth_data = {
                'application_type': 'private',
                'redirect_uris': ['https://webqx.healthcare/callback'],
                'client_name': 'WebQx Healthcare',
                'grant_types': ['client_credentials']
            }
            
            response = requests.post(auth_url, json=auth_data)
            if response.status_code == 200:
                auth_result = response.json()
                # Store client credentials
                return True
            return False
            
        except Exception as e:
            logger.error(f"OpenEMR authentication failed: {str(e)}")
            return False
    
    def get_patient(self, patient_id):
        """Get patient data from OpenEMR"""
        try:
            url = f"{self.base_url}/apis/default/fhir/Patient/{patient_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get patient {patient_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting patient from OpenEMR: {str(e)}")
            return None
    
    def create_patient(self, patient_data):
        """Create patient in OpenEMR"""
        try:
            url = f"{self.base_url}/apis/default/fhir/Patient"
            response = requests.post(url, json=patient_data, headers=self.headers)
            
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Failed to create patient: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating patient in OpenEMR: {str(e)}")
            return None
    
    def update_patient(self, patient_id, patient_data):
        """Update patient in OpenEMR"""
        try:
            url = f"{self.base_url}/apis/default/fhir/Patient/{patient_id}"
            response = requests.put(url, json=patient_data, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to update patient {patient_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating patient in OpenEMR: {str(e)}")
            return None
    
    def sync_patient(self, patient):
        """Sync patient data between WebQx and OpenEMR"""
        try:
            # Get latest data from OpenEMR
            openemr_data = self.get_patient(patient.openemr_patient_id)
            
            if openemr_data:
                # Update local patient data
                self._update_patient_from_fhir(patient, openemr_data)
                patient.last_sync = timezone.now()
                patient.save()
                
                logger.info(f"Successfully synced patient {patient.medical_record_number}")
                return patient
            else:
                logger.error(f"Failed to sync patient {patient.medical_record_number}")
                return None
                
        except Exception as e:
            logger.error(f"Error syncing patient: {str(e)}")
            return None
    
    def _update_patient_from_fhir(self, patient, fhir_data):
        """Update patient object from FHIR data"""
        try:
            # Update basic demographics
            if 'name' in fhir_data and fhir_data['name']:
                name = fhir_data['name'][0]
                if 'given' in name:
                    patient.first_name = name['given'][0]
                if 'family' in name:
                    patient.last_name = name['family']
            
            if 'gender' in fhir_data:
                patient.gender = fhir_data['gender']
            
            if 'birthDate' in fhir_data:
                from datetime import datetime
                patient.date_of_birth = datetime.strptime(fhir_data['birthDate'], '%Y-%m-%d').date()
            
            # Update contact information
            if 'telecom' in fhir_data:
                for contact in fhir_data['telecom']:
                    if contact.get('system') == 'phone':
                        patient.phone = contact.get('value', '')
                    elif contact.get('system') == 'email':
                        patient.email = contact.get('value', '')
            
            # Update address
            if 'address' in fhir_data and fhir_data['address']:
                address = fhir_data['address'][0]
                if 'line' in address:
                    patient.address_line1 = address['line'][0] if len(address['line']) > 0 else ''
                    patient.address_line2 = address['line'][1] if len(address['line']) > 1 else ''
                patient.city = address.get('city', '')
                patient.state = address.get('state', '')
                patient.zip_code = address.get('postalCode', '')
                patient.country = address.get('country', 'US')
            
        except Exception as e:
            logger.error(f"Error updating patient from FHIR data: {str(e)}")
    
    def get_encounters(self, patient_id):
        """Get encounters for a patient"""
        try:
            url = f"{self.base_url}/apis/default/fhir/Encounter"
            params = {'patient': patient_id}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Error getting encounters: {str(e)}")
            return None
    
    def create_encounter(self, encounter_data):
        """Create encounter in OpenEMR"""
        try:
            url = f"{self.base_url}/apis/default/fhir/Encounter"
            response = requests.post(url, json=encounter_data, headers=self.headers)
            
            if response.status_code == 201:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Error creating encounter: {str(e)}")
            return None
    
    def get_lab_results(self, patient_id):
        """Get lab results for a patient"""
        try:
            url = f"{self.base_url}/apis/default/fhir/Observation"
            params = {'patient': patient_id, 'category': 'laboratory'}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Error getting lab results: {str(e)}")
            return None
    
    def get_medications(self, patient_id):
        """Get medications for a patient"""
        try:
            url = f"{self.base_url}/apis/default/fhir/MedicationRequest"
            params = {'patient': patient_id}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Error getting medications: {str(e)}")
            return None


class FHIRConverter:
    """Utility class for converting between WebQx models and FHIR resources"""
    
    @staticmethod
    def patient_to_fhir(patient):
        """Convert Patient model to FHIR Patient resource"""
        return {
            "resourceType": "Patient",
            "id": str(patient.openemr_patient_id),
            "identifier": [{
                "value": patient.medical_record_number,
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "MR"
                    }]
                }
            }],
            "name": [{
                "family": patient.last_name,
                "given": [patient.first_name]
            }],
            "gender": patient.gender,
            "birthDate": str(patient.date_of_birth),
            "telecom": [
                {"system": "phone", "value": patient.phone},
                {"system": "email", "value": patient.email}
            ] if patient.phone or patient.email else [],
            "address": [{
                "line": [patient.address_line1, patient.address_line2],
                "city": patient.city,
                "state": patient.state,
                "postalCode": patient.zip_code,
                "country": patient.country
            }] if patient.address_line1 else []
        }
    
    @staticmethod
    def encounter_to_fhir(encounter):
        """Convert Encounter model to FHIR Encounter resource"""
        return {
            "resourceType": "Encounter",
            "id": str(encounter.openemr_encounter_id),
            "status": encounter.status,
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": encounter.encounter_class
            },
            "subject": {
                "reference": f"Patient/{encounter.patient.openemr_patient_id}"
            },
            "period": {
                "start": encounter.start_time.isoformat(),
                "end": encounter.end_time.isoformat() if encounter.end_time else None
            },
            "reasonCode": [{
                "text": encounter.chief_complaint
            }] if encounter.chief_complaint else []
        }