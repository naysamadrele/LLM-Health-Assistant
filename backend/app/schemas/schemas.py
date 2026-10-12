from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# --- User Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = "doctor" # doctor, nurse, admin, patient

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Patient Schemas ---
class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0, le=125)
    gender: str = Field(..., description="Male, Female, or Other")
    height: float = Field(..., ge=30, le=250, description="Height in cm")
    weight: float = Field(..., ge=2, le=500, description="Weight in kg")

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None

class PatientResponse(BaseModel):
    id: str
    creator_id: str
    name: str
    age: int
    gender: str
    height: float
    weight: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Symptom Schemas ---
class SymptomResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    is_red_flag: bool
    description: Optional[str] = None

    class Config:
        from_attributes = True

# --- Prediction Schemas ---
class PredictionResponse(BaseModel):
    id: str
    assessment_id: str
    disease: str
    probability: float
    risk_level: str
    shap_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Report Schemas ---
class ReportResponse(BaseModel):
    id: str
    assessment_id: str
    pdf_path: Optional[str] = None
    llm_diagnosis: str
    retrieved_evidence: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Assessment Schemas ---
class AssessmentCreate(BaseModel):
    patient_id: str
    blood_pressure_systolic: int = Field(..., ge=50, le=280)
    blood_pressure_diastolic: int = Field(..., ge=30, le=180)
    heart_rate: int = Field(..., ge=30, le=250)
    temperature: float = Field(..., ge=32.0, le=43.0, description="Temperature in Celsius")
    respiratory_rate: int = Field(..., ge=6, le=60)
    oxygen_saturation: int = Field(..., ge=50, le=100)
    blood_sugar: Optional[int] = Field(None, ge=10, le=600)
    
    symptoms: List[str] = Field(default_factory=list, description="List of symptom codes")
    
    # Nested dictionaries for lifestyle and medical history attributes
    lifestyle: Dict[str, Any] = Field(
        default_factory=dict, 
        description="e.g. {'smoking': 'never', 'alcohol': 'none', 'exercise': 'moderate', 'diet': 'balanced', 'sleep': '7-8h', 'stress': 'low'}"
    )
    medical_history: Dict[str, Any] = Field(
        default_factory=dict, 
        description="e.g. {'diabetes': false, 'hypertension': true, 'asthma': false, 'allergies': 'penicillin', 'medications': 'amlodipine'}"
    )

class AssessmentResponse(BaseModel):
    id: str
    patient_id: str
    user_id: str
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    temperature: float
    respiratory_rate: int
    oxygen_saturation: int
    blood_sugar: Optional[int]
    symptoms: List[str]
    lifestyle: Dict[str, Any]
    medical_history: Dict[str, Any]
    priority: str
    is_emergency: bool
    emergency_reason: Optional[str] = None
    created_at: datetime
    
    predictions: List[PredictionResponse] = []
    reports: List[ReportResponse] = []
    patient: Optional[PatientResponse] = None

    class Config:
        from_attributes = True
