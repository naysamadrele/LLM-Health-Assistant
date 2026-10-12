from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import Patient, User, AuditLog
from backend.app.schemas.schemas import PatientCreate, PatientResponse, PatientUpdate
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new patient record.
    """
    patient = Patient(
        name=patient_in.name,
        age=patient_in.age,
        gender=patient_in.gender,
        height=patient_in.height,
        weight=patient_in.weight,
        creator_id=current_user.id
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="CREATE_PATIENT",
        details=f"Created patient {patient.name} (ID: {patient.id})"
    )
    db.add(audit)
    db.commit()

    return patient

@router.get("/", response_model=List[PatientResponse])
def read_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all patients created by the current user.
    """
    # Doctors/nurses can access patient files
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients

@router.get("/{patient_id}", response_model=PatientResponse)
def read_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a patient by ID.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    patient_in: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update patient details.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    update_data = patient_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
        
    db.commit()
    db.refresh(patient)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="UPDATE_PATIENT",
        details=f"Updated details for patient ID: {patient.id}"
    )
    db.add(audit)
    db.commit()

    return patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a patient record.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    db.delete(patient)
    db.commit()

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="DELETE_PATIENT",
        details=f"Deleted patient ID: {patient_id}"
    )
    db.add(audit)
    db.commit()
    return None
