import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import Assessment, Patient, User, PredictionResult, Report, AuditLog
from backend.app.schemas.schemas import AssessmentCreate, AssessmentResponse
from backend.app.engine.rules_engine import ClinicalRulesEngine
from backend.app.ml.ml_pipeline import MLPredictionPipeline
from backend.app.ml.shap_explainer import SHAPExplainerEngine
from backend.app.rag.vector_store import VectorStoreManager
from backend.app.rag.ollama_client import OllamaRAGClient
from backend.app.api.deps import get_current_user
from backend.app.services.pdf_service import PDFReportGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_in: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Performs clinical rules check, executes machine learning disease classifiers,
    calculates SHAP explainability attributions, runs local semantic search,
    queries local Ollama RAG (Llama 3), and logs the final reports in PostgreSQL/SQLite.
    """
    # 1. Load patient demographics
    patient = db.query(Patient).filter(Patient.id == assessment_in.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # 2. Evaluate Clinical Rule Engine (overrides priority & detects immediate emergencies)
    vitals_dict = {
        "blood_pressure_systolic": assessment_in.blood_pressure_systolic,
        "blood_pressure_diastolic": assessment_in.blood_pressure_diastolic,
        "heart_rate": assessment_in.heart_rate,
        "temperature": assessment_in.temperature,
        "respiratory_rate": assessment_in.respiratory_rate,
        "oxygen_saturation": assessment_in.oxygen_saturation,
        "blood_sugar": assessment_in.blood_sugar
    }
    
    rules_result = ClinicalRulesEngine.evaluate(
        symptoms=assessment_in.symptoms,
        vitals=vitals_dict,
        patient_age=patient.age,
        medical_history=assessment_in.medical_history
    )

    # 3. Create core Assessment record
    assessment = Assessment(
        patient_id=assessment_in.patient_id,
        user_id=current_user.id,
        blood_pressure_systolic=assessment_in.blood_pressure_systolic,
        blood_pressure_diastolic=assessment_in.blood_pressure_diastolic,
        heart_rate=assessment_in.heart_rate,
        temperature=assessment_in.temperature,
        respiratory_rate=assessment_in.respiratory_rate,
        oxygen_saturation=assessment_in.oxygen_saturation,
        blood_sugar=assessment_in.blood_sugar,
        symptoms=assessment_in.symptoms,
        lifestyle=assessment_in.lifestyle,
        medical_history=assessment_in.medical_history,
        priority=rules_result["priority"],
        is_emergency=rules_result["is_emergency"],
        emergency_reason=", ".join(rules_result["reasons"]) if rules_result["reasons"] else None
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # 4. Trigger Machine Learning Inference & SHAP Explainability
    predictions_log = []
    shap_explanations = {}
    
    try:
        # Run ML predictions for Diabetes, Heart Disease, Stroke, Kidney Disease
        ml_results = MLPredictionPipeline.predict(patient, assessment)
        
        for disease, (prob, scaled_feats) in ml_results.items():
            # Classify risk level
            if prob > 0.70:
                risk_level = "HIGH"
            elif prob > 0.40:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            # Compute SHAP explainability payload for this prediction
            shap_data = SHAPExplainerEngine.explain_prediction(disease, scaled_feats, prob)
            shap_explanations[disease] = shap_data

            prediction_rec = PredictionResult(
                assessment_id=assessment.id,
                disease=disease,
                probability=prob,
                risk_level=risk_level,
                shap_data=shap_data
            )
            db.add(prediction_rec)
            predictions_log.append({
                "disease": disease,
                "probability": prob,
                "risk_level": risk_level
            })
    except Exception as e:
        logger.error(f"Error during ML/SHAP inference: {e}")
        # Fallback to saving standard low risk if models fail to load/evaluate
        for disease in ["Diabetes", "Heart Disease", "Stroke Risk", "Kidney Disease"]:
            prediction_rec = PredictionResult(
                assessment_id=assessment.id,
                disease=disease,
                probability=0.10,
                risk_level="LOW",
                shap_data={"natural_language_explanation": "ML prediction unavailable."}
            )
            db.add(prediction_rec)
            predictions_log.append({"disease": disease, "probability": 0.10, "risk_level": "LOW"})

    db.commit()

    # 5. RAG Guidelines Semantic Search & Local LLM Synthesis
    evidence = []
    try:
        # Query local ChromaDB with patient's active symptoms
        query_text = " ".join(assessment.symptoms) if assessment.symptoms else "general health symptoms vitals check"
        evidence = VectorStoreManager.search(query_text, limit=3)
    except Exception as e:
        logger.error(f"Error during ChromaDB guideline lookup: {e}")

    # Prepare user & patient dicts for the prompt
    patient_dict = {
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "height": patient.height,
        "weight": patient.weight
    }
    
    assessment_dict = {
        "symptoms": assessment.symptoms,
        "lifestyle": assessment.lifestyle,
        "medical_history": assessment.medical_history,
        "blood_pressure_systolic": assessment.blood_pressure_systolic,
        "blood_pressure_diastolic": assessment.blood_pressure_diastolic,
        "heart_rate": assessment.heart_rate,
        "temperature": assessment.temperature,
        "respiratory_rate": assessment.respiratory_rate,
        "oxygen_saturation": assessment.oxygen_saturation,
        "blood_sugar": assessment.blood_sugar,
        "priority": assessment.priority,
        "is_emergency": assessment.is_emergency,
        "emergency_reason": assessment.emergency_reason
    }

    # Query Ollama/Llama 3 (falls back to Python templates if Ollama offline)
    llm_report_text = OllamaRAGClient.query_llm(
        patient_data=patient_dict,
        assessment_data=assessment_dict,
        ml_predictions=predictions_log,
        shap_explanations=shap_explanations,
        retrieved_evidence=evidence
    )

    # 6. Save final PDF Report placeholder (real PDF generated via /report/{id}/pdf)
    report = Report(
        assessment_id=assessment.id,
        llm_diagnosis=llm_report_text,
        retrieved_evidence=evidence
    )
    db.add(report)
    db.commit()

    # 7. Audit log creation
    audit = AuditLog(
        user_id=current_user.id,
        action="RUN_ASSESSMENT",
        details=f"Completed clinical assessment {assessment.id} for {patient.name}. Priority: {assessment.priority}"
    )
    db.add(audit)
    db.commit()

    db.refresh(assessment)
    return assessment

@router.get("/", response_model=List[AssessmentResponse])
def read_assessments(
    skip: int = 0,
    limit: int = 100,
    patient_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves logged assessments. Optionally filters by patient_id.
    """
    query = db.query(Assessment)
    if patient_id:
        query = query.filter(Assessment.patient_id == patient_id)
        
    return query.order_by(Assessment.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{assessment_id}", response_model=AssessmentResponse)
def read_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a detailed assessment record (including symptoms, vitals, models, and LLM text).
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    return assessment

@router.get("/{assessment_id}/pdf")
def download_assessment_pdf(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates and returns a styled clinical PDF report download.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
        
    pdf_buffer = PDFReportGenerator.generate_assessment_pdf(assessment)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=assessment_report_{assessment_id}.pdf"}
    )
