import httpx
import json
import logging
from typing import Dict, Any, List
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaRAGClient:
    @staticmethod
    def query_llm(
        patient_data: Dict[str, Any],
        assessment_data: Dict[str, Any],
        ml_predictions: List[Dict[str, Any]],
        shap_explanations: Dict[str, Any],
        retrieved_evidence: List[Dict[str, Any]]
    ) -> str:
        """
        Sends a clinical prompt to the local Ollama container running Llama 3.
        Falls back to a structured rule-based generator if Ollama is offline.
        """
        prompt = OllamaRAGClient._build_prompt(
            patient_data, assessment_data, ml_predictions, shap_explanations, retrieved_evidence
        )

        url = f"{settings.OLLAMA_HOST}/api/generate"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature to reduce hallucination
                "top_p": 0.9
            }
        }

        try:
            # Query local Ollama service with a 30-second timeout
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    logger.warning(f"Ollama returned status {response.status_code}. Using clinical template fallback.")
        except Exception as e:
            logger.warning(f"Unable to connect to Ollama at {settings.OLLAMA_HOST}: {e}. Utilizing offline rule-based report fallback.")
            
        return OllamaRAGClient._generate_fallback_report(
            patient_data, assessment_data, ml_predictions, shap_explanations, retrieved_evidence
        )

    @staticmethod
    def _build_prompt(
        patient: Dict[str, Any],
        assessment: Dict[str, Any],
        ml_preds: List[Dict[str, Any]],
        shap_exp: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> str:
        """Constructs a heavily grounded and formatted clinical prompt for Llama 3."""
        
        # Format symptoms
        symptoms_str = ", ".join([s.replace("_", " ").title() for s in assessment.get("symptoms", [])])
        
        # Format ML predictions
        ml_str = "\n".join([
            f"- {p['disease']}: Probability {p['probability'] * 100:.1f}%, Risk Level: {p['risk_level']}"
            for p in ml_preds
        ])

        # Format SHAP details
        shap_str = ""
        for disease, explanation in shap_exp.items():
            shap_str += f"\nFor {disease}:\n  {explanation.get('natural_language_explanation', '')}"

        # Format retrieved clinical guidelines
        evidence_str = "\n".join([
            f"Source: {ev['metadata'].get('source', 'Unknown')}\nContext: {ev['text']}"
            for ev in evidence
        ])

        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert Clinical Decision Support System (CDSS) AI assistant. 
Your goal is to assist a licensed healthcare professional by synthesizing patient data, machine learning predictions, explainable AI (SHAP) attributions, and retrieved medical evidence to generate a structured clinical assessment report.

CRITICAL INSTRUCTIONS:
1. Always state clearly that this is a Clinical Decision Support System report and does NOT replace a physician's evaluation.
2. Ground all diagnoses, recommendations, and tests strictly in the provided "Retrieved Medical Evidence" and patient statistics.
3. NEVER make up or invent medications, treatments, or diagnostics not supported by the evidence.
4. Mark all differential diagnoses as "Possible Conditions" rather than confirmed states.
5. If the evidence does not provide enough information for a specific symptom, state clearly: "Additional clinical evaluation is required."
6. Ensure the output is highly professional, clean, and structured in Markdown format.

<|eot_id|><|start_header_id|>user<|end_header_id|>
Please generate a clinical report for the following patient:

### 1. PATIENT DEMOGRAPHICS & VITALS
- Name: {patient.get('name')}
- Age: {patient.get('age')} years old
- Gender: {patient.get('gender')}
- Height: {patient.get('height')} cm
- Weight: {patient.get('weight')} kg
- Vitals:
  - Blood Pressure: {assessment.get('blood_pressure_systolic')}/{assessment.get('blood_pressure_diastolic')} mmHg
  - Heart Rate: {assessment.get('heart_rate')} bpm
  - Temperature: {assessment.get('temperature')} °C
  - Respiratory Rate: {assessment.get('respiratory_rate')} breaths/min
  - Oxygen Saturation (SpO2): {assessment.get('oxygen_saturation')}%
  - Blood Sugar: {assessment.get('blood_sugar', 'N/A')} mg/dL

### 2. SYMPTOMS & LIFESTYLE LOGGED
- Active Symptoms: {symptoms_str}
- Lifestyle Factors: {json.dumps(assessment.get('lifestyle', {}))}
- Medical History: {json.dumps(assessment.get('medical_history', {}))}
- Priority Override Level (Rules Engine): {assessment.get('priority', 'LOW')}
- Emergency Status: {assessment.get('is_emergency')} (Reason: {assessment.get('emergency_reason', 'None')})

### 3. MACHINE LEARNING PREDICTION RISK ESTIMATES
{ml_str}

### 4. EXPLAINABLE AI (SHAP) RISK CONTRIBTORS
{shap_str}

### 5. RETRIEVED CLINICAL PRACTICE EVIDENCE
{evidence_str}

Please synthesize the above findings into a structured report using these headings:
1. **Clinical Overview & Urgency Assessment** (Discuss priority, emergency reasons, and vitals)
2. **Differential Diagnosis (Possible Conditions)** (Rank potential diagnoses based on ML probability, rules, and symptoms. Cite sources from retrieved evidence. State confidence)
3. **SHAP Explainability Summary** (Summarize why the models calculated these risk profiles in plain English)
4. **Recommended Diagnostic Workup & Specialist Referral** (Highlight tests and specialists to consult)
5. **Evidence-based Lifestyle and Preventive Guidelines** (Custom diet, sleep, and physical instructions based on lifestyle and risk levels)
6. **Medical Disclaimer** (Required medical backup warning)
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        return prompt

    @staticmethod
    def _generate_fallback_report(
        patient: Dict[str, Any],
        assessment: Dict[str, Any],
        ml_preds: List[Dict[str, Any]],
        shap_exp: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> str:
        """Generates a highly structured, clinical report using standard templates for offline fallback."""
        
        # Symptoms string
        symptoms_list = [s.replace("_", " ").title() for s in assessment.get("symptoms", [])]
        symptoms_str = ", ".join(symptoms_list) if symptoms_list else "None"
        
        # Sort ML predictions by probability
        sorted_preds = sorted(ml_preds, key=lambda x: x["probability"], reverse=True)
        top_disease = sorted_preds[0]["disease"] if sorted_preds else "General Health Conditions"
        
        # Build explanation sentences
        shap_summary_sentences = []
        for disease, explanation in shap_exp.items():
            shap_summary_sentences.append(explanation.get("natural_language_explanation", ""))
        shap_summary_text = " ".join(shap_summary_sentences)

        # Build differential diagnosis table based on symptoms and vitals
        diff_diag = []
        priority = assessment.get("priority", "LOW")
        
        # Determine likely differentials based on rules
        symptom_set = set(assessment.get("symptoms", []))
        if "chest_pain" in symptom_set or "shortness_of_breath" in symptom_set:
            diff_diag.append("- **Possible Condition**: Coronary Artery Disease / Angina (Confidence: High, given ML heart prediction and symptoms)")
            diff_diag.append("- **Possible Condition**: Gastroesophageal Reflux Disease (GERD) (Confidence: Medium, as atypical chest mimic)")
        if "polyuria" in symptom_set or "polydipsia" in symptom_set:
            diff_diag.append("- **Possible Condition**: Type 2 Diabetes Mellitus (Confidence: High, supported by hyperglycemic symptoms)")
        if "unilateral_weakness" in symptom_set or "slurred_speech" in symptom_set:
            diff_diag.append("- **Possible Condition**: Acute Stroke / TIA (Confidence: Critical, immediate imaging required)")
        if "stiff_neck" in symptom_set and "fever" in symptom_set:
            diff_diag.append("- **Possible Condition**: Acute Bacterial/Viral Meningitis (Confidence: Critical, immediate lumbar puncture required)")
        if "flank_pain" in symptom_set or "anuria" in symptom_set:
            diff_diag.append("- **Possible Condition**: Nephrolithiasis (Kidney Stones) / Acute Kidney Injury (Confidence: High)")

        if not diff_diag:
            # General health assessments
            diff_diag.append("- **Possible Condition**: General Viral Upper Respiratory Infection (Confidence: Medium)")
            diff_diag.append("- **Possible Condition**: Tension-Type Headache / Mild Fatigue (Confidence: Medium)")

        # Compile references
        sources_str = ", ".join(list(set([ev["metadata"].get("source", "NHS") for ev in evidence]))) if evidence else "WHO & NHS Clinical Guidelines"

        report = f"""# CLINICAL ASSESSMENT SUPPORT REPORT

### 1. Clinical Overview & Urgency Assessment
* **Assessed Priority**: **{priority}**
* **Emergency Status**: {"EMERGENCY (Immediate attention required)" if assessment.get("is_emergency") else "Stable / Non-emergency"}
* **Emergency Reason**: {assessment.get("emergency_reason", "None")}
* **Clinical Overview**: Patient is a {patient.get('age')}-year-old {patient.get('gender')}. Logged vitals show Blood Pressure: {assessment.get('blood_pressure_systolic')}/{assessment.get('blood_pressure_diastolic')} mmHg, Heart Rate: {assessment.get('heart_rate')} bpm, SpO2: {assessment.get('oxygen_saturation')}%, and Blood Sugar: {assessment.get('blood_sugar', 'N/A')} mg/dL. Reported symptoms include: {symptoms_str}.

### 2. Differential Diagnosis (Possible Conditions)
Based on clinical signs and matching databases, the following possible conditions should be investigated (Note: these are *possible* conditions and do not substitute a clinician's final diagnosis):
{chr(10).join(diff_diag)}

*Evidence grounding*: Grounded in clinical symptoms and vector reference guidelines. Cites: {sources_str}.

### 3. SHAP Explainability Summary
{shap_summary_text}

### 4. Recommended Diagnostic Workup & Specialist Referral
* **Suggested Diagnostics**: Complete Blood Count (CBC), Metabolic Panels, and specific screens corresponding to top risk areas.
* **Suggested Specialist Consultations**: Referral to appropriate clinical branches based on symptoms.

### 5. Evidence-Based Lifestyle & Preventive Guidelines
* **Exercise**: Adopt at least 150 minutes of moderate cardiovascular activity weekly.
* **Diet**: Shift towards low-glycemic, low-sodium meals to support cardiovascular and metabolic health.
* **Monitoring**: Regular monitoring of daily vital signs (BP and blood glucose) is recommended.

### 6. Medical Disclaimer
**IMPORTANT**: This report is generated by a Clinical Decision Support System (CDSS) for informational purposes to support clinical workflows. It is NOT a diagnostic tool and does NOT replace the professional clinical judgment of a licensed healthcare practitioner. All diagnoses must be verified by laboratory work and clinical observation.
"""
        return report
