from backend.app.rag.vector_store import VectorStoreManager
import logging

logger = logging.getLogger(__name__)

CLINICAL_GUIDELINES = [
    # --- Diabetes ---
    {
        "text": "Diabetes diagnosis criteria: Fasting plasma glucose >= 126 mg/dL (7.0 mmol/L), or 2-hour post-prandial glucose >= 200 mg/dL (11.1 mmol/L) during an oral glucose tolerance test, or HbA1c >= 6.5%. Symptoms of severe hyperglycemia include polyuria (excessive urination), polydipsia (excessive thirst), and polyphagia (excessive hunger) combined with unexplained weight loss. Classic screening is advised for adults with BMI >= 25 kg/m2 who have one or more additional risk factors such as physical inactivity, hypertension, or family history of diabetes.",
        "source": "ADA Guidelines 2024 - Section 2",
        "category": "Endocrinology",
        "id": "kb_diabetes_001"
    },
    {
        "text": "First-line lifestyle interventions for Type 2 Diabetes include physical activity of at least 150 minutes per week of moderate-intensity aerobic exercise, a Mediterranean-style diet low in simple carbohydrates and saturated fats, and weight loss targeting 5-10% of initial body weight. Pharmacological treatment usually starts with Metformin, unless contraindicated (e.g., severe renal impairment with GFR < 30 ml/min). Annual screening for diabetic complications (nephropathy, retinopathy, and peripheral neuropathy) is highly recommended.",
        "source": "ADA Guidelines 2024 - Section 9",
        "category": "Endocrinology",
        "id": "kb_diabetes_002"
    },

    # --- Cardiovascular / Heart Disease ---
    {
        "text": "Hypertension is classified by the ACC/AHA as Stage 1 if systolic blood pressure is 130-139 mmHg or diastolic is 80-89 mmHg. Stage 2 hypertension is defined as systolic BP >= 140 mmHg or diastolic BP >= 90 mmHg. Hypertensive crisis occurs when blood pressure suddenly exceeds 180/120 mmHg, requiring immediate emergency evaluation if target organ damage (e.g., chest pain, shortness of breath, back pain, numbness, vision changes) is present. First-line medications include ACE inhibitors, ARBs, Calcium Channel Blockers, or thiazide diuretics.",
        "source": "ACC/AHA Hypertension Guidelines 2017",
        "category": "Cardiology",
        "id": "kb_cardio_001"
    },
    {
        "text": "Coronary Artery Disease (CAD) risk assessment relies heavily on factors including age, male gender, smoking status, total cholesterol, HDL cholesterol, systolic blood pressure, and diabetes. Angina is characterized by central chest discomfort (pressure, squeezing, heaviness) radiating to the left arm, neck, or jaw, precipitated by exertion or stress and relieved by rest or nitroglycerin. Atypical chest pain is common in women, older adults, and diabetic patients, who may present primarily with dyspnea, fatigue, or nausea.",
        "source": "ESC Guidelines on Chronic Coronary Syndromes 2019",
        "category": "Cardiology",
        "id": "kb_cardio_002"
    },
    {
        "text": "Acute Coronary Syndrome (ACS) emergency warning signs: crushing retrosternal chest pain lasting more than 15 minutes, not relieved by rest or nitroglycerin, accompanied by diaphoresis (sweating), dyspnea (shortness of breath), palpitations, or syncope (fainting). In the presence of these symptoms, immediate activation of emergency medical services is mandatory. An electrocardiogram (ECG) must be performed within 10 minutes of first medical contact, and serial cardiac troponins should be analyzed.",
        "source": "AHA/ACC Guidelines for ACS 2021",
        "category": "Cardiology",
        "id": "kb_cardio_003"
    },

    # --- Stroke ---
    {
        "text": "Acute ischemic stroke is suspected using the FAST tool: Facial drooping (one side of the face droops or is numb), Arm weakness (one arm drifts downward when raised), Speech difficulty (slurred speech, difficulty speaking or understanding), and Time to call emergency services. Intravenous thrombolysis (tPA) should be administered within 3 to 4.5 hours of symptom onset for eligible patients to minimize long-term disability. Emergency brain imaging (CT scan without contrast) must be performed immediately upon hospital arrival.",
        "source": "AHA/ASA Stroke Guidelines 2019",
        "category": "Neurology",
        "id": "kb_stroke_001"
    },
    {
        "text": "Primary and secondary stroke prevention strategies focus on aggressive blood pressure control (target BP < 130/80 mmHg), lipid lowering using high-intensity statins, antiplatelet therapy (e.g., aspirin 81mg daily) for non-cardioembolic sources, and anticoagulation (e.g., warfarin or DOACs) for patients with atrial fibrillation. Additional lifestyle modifications include smoking cessation, restriction of alcohol consumption, and adopting a low-sodium diet.",
        "source": "AHA/ASA Secondary Stroke Prevention 2021",
        "category": "Neurology",
        "id": "kb_stroke_002"
    },

    # --- Kidney Disease ---
    {
        "text": "Chronic Kidney Disease (CKD) is defined as abnormalities of kidney structure or function, present for more than 3 months, with implications for health. It is classified based on Cause, GFR category, and Albuminuria category (CGA staging). GFR categories: G1 (>=90 normal), G2 (60-89 mild), G3a (45-59 mild-to-moderate), G3b (30-44 moderate-to-severe), G4 (15-29 severe kidney damage), and G5 (<15 kidney failure / ESRD). Major causes include diabetes mellitus and long-standing hypertension.",
        "source": "KDIGO CKD Guidelines 2012",
        "category": "Nephrology",
        "id": "kb_kidney_001"
    },
    {
        "text": "Management of Chronic Kidney Disease (CKD) focuses on slowing progression. Key interventions are strict blood pressure control with ACE inhibitors or ARBs (first-line in patients with proteinuria/albuminuria), optimizing glycemic control in diabetic patients, avoiding nephrotoxic drugs (such as NSAIDs, e.g., ibuprofen, naproxen, and certain antibiotics), and adjusting medication dosages based on estimated GFR. Dietary protein restriction (0.6-0.8 g/kg/day) may be recommended in advanced stages.",
        "source": "KDIGO CKD Guidelines 2023 Update",
        "category": "Nephrology",
        "id": "kb_kidney_002"
    },

    # --- General Red Flags (Meningitis, Sepsis, Severe Infections) ---
    {
        "text": "Meningitis clinical signs in adults include a high fever, sudden severe headache, and neck stiffness (nuchal rigidity). Other features are photophobia (light sensitivity), confusion, altered mental status, and a non-blanching purpuric rash (characteristic of meningococcal septicaemia). Any suspicion of meningitis is a medical emergency requiring an immediate lumbar puncture to examine cerebrospinal fluid (CSF) and prompt initiation of empiric intravenous antibiotics.",
        "source": "NHS Guidelines on Meningitis 2022",
        "category": "Infectious Disease",
        "id": "kb_general_001"
    },
    {
        "text": "Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. Warning signs include high or very low body temperature, severe shivering or muscle pain, slurred speech or confusion, extreme breathlessness, skin discoloration or mottling, and passing no urine in a day. It is evaluated clinically using the quick SOFA (qSOFA) score which assesses respiratory rate >= 22/min, altered mentation, and systolic blood pressure <= 100 mmHg.",
        "source": "Surviving Sepsis Campaign Guidelines 2021",
        "category": "Infectious Disease",
        "id": "kb_general_002"
    }
]

def ingest_guidelines():
    """Seeds the ChromaDB vector database with standard medical guidelines."""
    try:
        collection = VectorStoreManager.get_collection()
        count = collection.count()
        
        if count > 0:
            print(f"Vector Database already initialized with {count} clinical reference chunks.")
            return

        print("Ingesting clinical guidelines into local vector store...")
        texts = [item["text"] for item in CLINICAL_GUIDELINES]
        metadatas = [
            {"source": item["source"], "category": item["category"]}
            for item in CLINICAL_GUIDELINES
        ]
        ids = [item["id"] for item in CLINICAL_GUIDELINES]

        VectorStoreManager.add_documents(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Ingested {len(CLINICAL_GUIDELINES)} documents into ChromaDB.")
    except Exception as e:
        logger.error(f"Error during guideline vector ingestion: {e}")
        raise e

if __name__ == "__main__":
    ingest_guidelines()
