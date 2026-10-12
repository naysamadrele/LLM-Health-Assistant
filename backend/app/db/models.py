import datetime
import uuid
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="doctor")  # doctor, nurse, admin, patient
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patients = relationship("Patient", back_populates="creator")
    assessments = relationship("Assessment", back_populates="assessor")
    audit_logs = relationship("AuditLog", back_populates="user")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=generate_uuid)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)  # Male, Female, Other
    height = Column(Float, nullable=False)   # in cm
    weight = Column(Float, nullable=False)   # in kg
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    creator = relationship("User", back_populates="patients")
    assessments = relationship("Assessment", back_populates="patient", cascade="all, delete-orphan")

class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False) # e.g. "fever", "chest_pain"
    name = Column(String, nullable=False)
    category = Column(String, nullable=False) # e.g. Respiratory, Cardiovascular, General
    is_red_flag = Column(Boolean, default=False)
    description = Column(String, nullable=True)

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Vital Signs
    blood_pressure_systolic = Column(Integer, nullable=False)
    blood_pressure_diastolic = Column(Integer, nullable=False)
    heart_rate = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False) # In Celsius
    respiratory_rate = Column(Integer, nullable=False)
    oxygen_saturation = Column(Integer, nullable=False) # In percentage
    blood_sugar = Column(Integer, nullable=True) # In mg/dL
    
    # Symptoms: stored as a list of symptom codes (JSON array of strings)
    symptoms = Column(JSON, nullable=False, default=list) 
    
    # Lifestyle parameters: smoking, alcohol, exercise, diet, sleep, stress
    lifestyle = Column(JSON, nullable=False, default=dict)
    
    # Medical history: diabetes, hypertension, asthma, heart_disease, kidney_disease, liver_disease, allergies, current_medications
    medical_history = Column(JSON, nullable=False, default=dict)
    
    # Priority & Emergency Overrides from Rule Engine
    priority = Column(String, default="LOW") # LOW, MEDIUM, HIGH, EMERGENCY
    is_emergency = Column(Boolean, default=False)
    emergency_reason = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="assessments")
    assessor = relationship("User", back_populates="assessments")
    predictions = relationship("PredictionResult", back_populates="assessment", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="assessment", cascade="all, delete-orphan")

class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    disease = Column(String, nullable=False) # e.g. "Diabetes", "Heart Disease", "Stroke Risk", "Kidney Disease"
    probability = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False) # LOW, MEDIUM, HIGH
    shap_data = Column(JSON, nullable=True) # JSON payload representing feature importances for this prediction
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    assessment = relationship("Assessment", back_populates="predictions")

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    pdf_path = Column(String, nullable=True)
    llm_diagnosis = Column(Text, nullable=False)
    retrieved_evidence = Column(JSON, nullable=True) # References to loaded literature in ChromaDB
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    assessment = relationship("Report", back_populates="reports", foreign_keys=[assessment_id], remote_side=[id]) # self reference fix
    
    # Correct relationship mapping to Assessment
    assessment = relationship("Assessment", back_populates="reports")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
