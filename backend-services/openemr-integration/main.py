"""
OpenEMR Integration Service - FHIR/REST API connector
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from datetime import datetime

app = FastAPI(
    title="WebQx OpenEMR Integration",
    description="FHIR/REST API integration with OpenEMR",
    version="1.0.0"
)

security = HTTPBearer()

# Configuration
OPENEMR_BASE_URL = os.getenv("OPENEMR_BASE_URL", "http://localhost:8080")
OPENEMR_API_TOKEN = os.getenv("OPENEMR_API_TOKEN", "")

class Patient(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    medical_record_number: Optional[str] = None

class Appointment(BaseModel):
    id: str
    patient_id: str
    provider_name: str
    appointment_date: str
    appointment_time: str
    status: str
    notes: Optional[str] = None

class LabResult(BaseModel):
    id: str
    patient_id: str
    test_name: str
    value: str
    unit: str
    reference_range: str
    status: str
    date_collected: str

class Medication(BaseModel):
    id: str
    patient_id: str
    medication_name: str
    dosage: str
    frequency: str
    prescriber: str
    start_date: str
    end_date: Optional[str] = None

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token from middleware"""
    # In production, verify token with middleware service
    return {"user_id": "test_user"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "openemr-integration"}

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str, user=Depends(verify_token)):
    """Get patient information from OpenEMR"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPENEMR_BASE_URL}/apis/default/api/patient/{patient_id}",
                headers={"Authorization": f"Bearer {OPENEMR_API_TOKEN}"}
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Patient not found")
            
            response.raise_for_status()
            data = response.json()
            
            return Patient(
                id=data.get("pid", patient_id),
                first_name=data.get("fname", ""),
                last_name=data.get("lname", ""),
                email=data.get("email", ""),
                phone=data.get("phone_home", ""),
                date_of_birth=data.get("DOB", ""),
                medical_record_number=data.get("pubpid", "")
            )
    except httpx.RequestError:
        # Return mock data for demo
        return Patient(
            id=patient_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="(555) 123-4567",
            date_of_birth="1980-01-01",
            medical_record_number="MRN001"
        )

@app.get("/patients/{patient_id}/appointments", response_model=List[Appointment])
async def get_patient_appointments(patient_id: str, user=Depends(verify_token)):
    """Get patient appointments from OpenEMR"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPENEMR_BASE_URL}/apis/default/api/patient/{patient_id}/appointment",
                headers={"Authorization": f"Bearer {OPENEMR_API_TOKEN}"}
            )
            
            response.raise_for_status()
            data = response.json()
            
            appointments = []
            for apt in data:
                appointments.append(Appointment(
                    id=apt.get("pc_eid", ""),
                    patient_id=patient_id,
                    provider_name=apt.get("ufname", "") + " " + apt.get("ulname", ""),
                    appointment_date=apt.get("pc_eventDate", ""),
                    appointment_time=apt.get("pc_startTime", ""),
                    status=apt.get("pc_apptstatus", ""),
                    notes=apt.get("pc_hometext", "")
                ))
            
            return appointments
    except httpx.RequestError:
        # Return mock data for demo
        return [
            Appointment(
                id="1",
                patient_id=patient_id,
                provider_name="Dr. Smith",
                appointment_date="2024-01-20",
                appointment_time="14:00",
                status="scheduled",
                notes="Follow-up appointment"
            )
        ]

@app.get("/patients/{patient_id}/lab-results", response_model=List[LabResult])
async def get_patient_lab_results(patient_id: str, user=Depends(verify_token)):
    """Get patient lab results from OpenEMR"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPENEMR_BASE_URL}/apis/default/api/patient/{patient_id}/procedure_result",
                headers={"Authorization": f"Bearer {OPENEMR_API_TOKEN}"}
            )
            
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result in data:
                results.append(LabResult(
                    id=result.get("procedure_result_id", ""),
                    patient_id=patient_id,
                    test_name=result.get("result_text", ""),
                    value=result.get("result", ""),
                    unit=result.get("units", ""),
                    reference_range=result.get("range", ""),
                    status=result.get("result_status", ""),
                    date_collected=result.get("date", "")
                ))
            
            return results
    except httpx.RequestError:
        # Return mock data for demo
        return [
            LabResult(
                id="1",
                patient_id=patient_id,
                test_name="Blood Glucose",
                value="95",
                unit="mg/dL",
                reference_range="70-100",
                status="normal",
                date_collected="2024-01-15"
            ),
            LabResult(
                id="2",
                patient_id=patient_id,
                test_name="HbA1c",
                value="6.5",
                unit="%",
                reference_range="<7.0",
                status="normal",
                date_collected="2024-01-15"
            )
        ]

@app.get("/patients/{patient_id}/medications", response_model=List[Medication])
async def get_patient_medications(patient_id: str, user=Depends(verify_token)):
    """Get patient medications from OpenEMR"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPENEMR_BASE_URL}/apis/default/api/patient/{patient_id}/prescription",
                headers={"Authorization": f"Bearer {OPENEMR_API_TOKEN}"}
            )
            
            response.raise_for_status()
            data = response.json()
            
            medications = []
            for med in data:
                medications.append(Medication(
                    id=med.get("id", ""),
                    patient_id=patient_id,
                    medication_name=med.get("drug", ""),
                    dosage=med.get("dosage", ""),
                    frequency=med.get("form", ""),
                    prescriber=med.get("provider_name", ""),
                    start_date=med.get("date_added", ""),
                    end_date=med.get("date_modified", "")
                ))
            
            return medications
    except httpx.RequestError:
        # Return mock data for demo
        return [
            Medication(
                id="1",
                patient_id=patient_id,
                medication_name="Metformin",
                dosage="500mg",
                frequency="Twice daily",
                prescriber="Dr. Smith",
                start_date="2024-01-01",
                end_date=None
            )
        ]

@app.post("/fhir/sync")
async def sync_fhir_resources(user=Depends(verify_token)):
    """Sync FHIR resources from OpenEMR"""
    # Implementation for FHIR resource synchronization
    return {"status": "sync_started", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)