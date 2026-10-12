from typing import List, Dict, Any, Tuple

class ClinicalRulesEngine:
    @staticmethod
    def evaluate(
        symptoms: List[str],
        vitals: Dict[str, Any],
        patient_age: int,
        medical_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates clinical rules on symptoms and vital signs to determine priority level
        and emergency actions. Overrides machine learning results if red flags are present.
        """
        is_emergency = False
        priority = "LOW"
        reasons = []
        recommended_tests = []
        recommended_specialists = []

        # Extract vitals with defaults
        systolic = vitals.get("blood_pressure_systolic")
        diastolic = vitals.get("blood_pressure_diastolic")
        heart_rate = vitals.get("heart_rate")
        temp = vitals.get("temperature")
        resp_rate = vitals.get("respiratory_rate")
        spo2 = vitals.get("oxygen_saturation")
        blood_sugar = vitals.get("blood_sugar")

        # 1. Evaluate Vital Sign Red Flags
        if spo2 is not None and spo2 < 90:
            is_emergency = True
            priority = "EMERGENCY"
            reasons.append("Severe Hypoxia (Oxygen Saturation < 90%)")
            recommended_tests.append("Arterial Blood Gas (ABG)")
            recommended_specialists.append("Pulmonologist / Emergency Physician")

        elif spo2 is not None and spo2 < 94:
            priority = "HIGH"
            reasons.append("Mild Hypoxia (Oxygen Saturation 90-93%)")
            recommended_tests.append("Chest X-Ray")
            recommended_specialists.append("Pulmonologist")

        if systolic is not None and diastolic is not None:
            if systolic > 180 or diastolic > 120:
                is_emergency = True
                priority = "EMERGENCY"
                reasons.append("Hypertensive Crisis (BP > 180/120 mmHg)")
                recommended_tests.extend(["Electrocardiogram (ECG)", "Serum Creatinine", "Cardiac Troponin"])
                recommended_specialists.append("Cardiologist / Emergency Physician")
            elif systolic < 90:
                priority = "HIGH"
                is_emergency = True # Shock risk
                reasons.append("Severe Hypotension (Systolic BP < 90 mmHg) - Risk of Shock")
                recommended_tests.append("Basic Metabolic Panel (BMP)")
                recommended_specialists.append("Emergency Physician")

        if heart_rate is not None:
            if heart_rate > 130:
                priority = "HIGH"
                reasons.append("Severe Tachycardia (Heart Rate > 130 bpm)")
                recommended_tests.append("Electrocardiogram (ECG)")
                recommended_specialists.append("Cardiologist")
            elif heart_rate < 45:
                priority = "HIGH"
                reasons.append("Severe Bradycardia (Heart Rate < 45 bpm)")
                recommended_tests.append("Electrocardiogram (ECG)")
                recommended_specialists.append("Cardiologist")

        if resp_rate is not None:
            if resp_rate > 30:
                is_emergency = True
                priority = "EMERGENCY"
                reasons.append("Severe Tachypnea (Respiratory Rate > 30 breaths/min) - Impending Respiratory Failure")
                recommended_tests.append("Chest X-Ray / ABG")
                recommended_specialists.append("Pulmonologist")
            elif resp_rate < 8:
                is_emergency = True
                priority = "EMERGENCY"
                reasons.append("Bradypnea (Respiratory Rate < 8 breaths/min) - Severe Respiratory Depression")
                recommended_specialists.append("Emergency Physician")

        if temp is not None:
            if temp > 40.0:
                is_emergency = True
                priority = "EMERGENCY"
                reasons.append("Severe Hyperpyrexia (Temperature > 40.0°C / 104°F)")
                recommended_tests.extend(["Blood Cultures", "Complete Blood Count (CBC)"])
                recommended_specialists.append("Infectious Disease Specialist")
            elif temp < 35.0:
                priority = "HIGH"
                reasons.append("Hypothermia (Temperature < 35.0°C / 95°F)")
                recommended_specialists.append("Emergency Physician")

        if blood_sugar is not None:
            if blood_sugar < 50:
                is_emergency = True
                priority = "EMERGENCY"
                reasons.append("Severe Hypoglycemia (Blood Sugar < 50 mg/dL)")
                recommended_specialists.append("Endocrinologist / Emergency Physician")
            elif blood_sugar > 350:
                priority = "HIGH"
                reasons.append("Severe Hyperglycemia (Blood Sugar > 350 mg/dL) - Risk of DKA/HHS")
                recommended_tests.extend(["Urine Ketones", "HbA1c", "Arterial Blood Gas (ABG)"])
                recommended_specialists.append("Endocrinologist")

        # 2. Evaluate Symptom-Based Red Flags
        symptom_set = set(symptoms)

        # Chest Pain + Dyspnea -> Suspected Heart Attack or PE
        if "chest_pain" in symptom_set and "shortness_of_breath" in symptom_set:
            is_emergency = True
            priority = "EMERGENCY"
            reasons.append("Combined Chest Pain & Shortness of Breath - Suspected Cardiac Event or PE")
            recommended_tests.extend(["12-Lead ECG", "Cardiac Troponin I", "D-Dimer"])
            recommended_specialists.append("Cardiologist")

        # Fever + Stiff Neck -> Suspected Meningitis
        if "stiff_neck" in symptom_set and ("fever" in symptom_set or "high_fever" in symptom_set):
            is_emergency = True
            priority = "EMERGENCY"
            reasons.append("Fever associated with Stiff Neck - Suspected Meningitis")
            recommended_tests.append("Lumbar Puncture (CSF analysis)")
            recommended_specialists.append("Neurologist / Infectious Disease Specialist")

        # Stroke FAST symptoms
        if "unilateral_weakness" in symptom_set or "slurred_speech" in symptom_set:
            is_emergency = True
            priority = "EMERGENCY"
            reasons.append("Acute neurological deficits (one-sided weakness/slurred speech) - Suspected Stroke")
            recommended_tests.append("Non-contrast Head CT Scan")
            recommended_specialists.append("Neurologist / Stroke Specialist")

        if "sudden_severe_headache" in symptom_set:
            is_emergency = True
            priority = "EMERGENCY"
            reasons.append("Sudden severe headache ('Thunderclap') - Suspected Intracranial Hemorrhage")
            recommended_tests.append("Head CT Scan")
            recommended_specialists.append("Neurologist / Neurosurgeon")

        if "suicidal_ideation" in symptom_set:
            is_emergency = True
            priority = "EMERGENCY"
            reasons.append("Suicidal ideation - Psychiatric Emergency requiring immediate support")
            recommended_specialists.append("Psychiatrist / Crisis Team")

        if "anuria" in symptom_set:
            is_emergency = True
            priority = "EMERGENCY"
            reasons.append("Inability to urinate (Anuria) - Suspected Acute Kidney Injury or obstruction")
            recommended_tests.extend(["Renal Ultrasound", "Serum Creatinine & Electrolytes"])
            recommended_specialists.append("Urologist / Nephrologist")

        if "vision_loss" in symptom_set:
            is_emergency = True
            priority = "EMERGENCY"
            reasons.append("Sudden vision loss - Ocular Emergency")
            recommended_tests.append("Fundoscopy")
            recommended_specialists.append("Ophthalmologist")

        # Secondary high-priority symptom checks (if not already emergency)
        if priority != "EMERGENCY":
            high_priority_symptoms = {
                "hemoptysis": ("Coughing up blood", ["Chest CT", "Bronchoscopy"], "Pulmonologist"),
                "severe_abdominal_pain": ("Severe abdominal pain", ["Abdominal CT Scan", "Amylase/Lipase"], "General Surgeon"),
                "jaundice": ("Jaundice / yellowing of eyes/skin", ["Liver Function Tests (LFTs)", "Abdominal Ultrasound"], "Gastroenterologist/Hepatologist"),
                "melena": ("Black/tarry stools (suspected upper GI bleed)", ["Upper Endoscopy", "Hemoglobin level"], "Gastroenterologist"),
                "hematochezia": ("Bright red blood in stool (suspected lower GI bleed)", ["Colonoscopy"], "Gastroenterologist"),
                "double_vision": ("Double vision (Diplopia)", ["Brain MRI"], "Neurologist / Ophthalmologist")
            }
            
            for sym, (desc, tests, specialist) in high_priority_symptoms.items():
                if sym in symptom_set:
                    priority = "HIGH"
                    reasons.append(f"{desc}")
                    recommended_tests.extend(tests)
                    recommended_specialists.append(specialist)

        # 3. Medium Priority Rules
        if priority == "LOW":
            medium_symptoms = ["fever", "cough", "vomiting", "diarrhea", "pelvic_pain", "flank_pain", "palpitations", "numbness"]
            matching_medium = [s for s in medium_symptoms if s in symptom_set]
            if len(matching_medium) >= 2 or len(symptom_set) >= 4:
                priority = "MEDIUM"
                reasons.append(f"Multiple moderate symptoms present ({', '.join(matching_medium)})")

            # Check vitals for medium
            if systolic is not None and (systolic >= 140 or systolic < 100):
                priority = "MEDIUM"
                reasons.append("Elevated or borderline low Blood Pressure")
                
            if temp is not None and (temp > 38.0 or temp < 36.0):
                priority = "MEDIUM"
                reasons.append("Mild fever or borderline hypothermia")

        # Deduplicate recommendations
        recommended_tests = list(set(recommended_tests))
        recommended_specialists = list(set(recommended_specialists))

        # Defaults for specialists and tests if empty
        if not recommended_specialists:
            if priority in ["EMERGENCY", "HIGH"]:
                recommended_specialists.append("Emergency Physician / General Practitioner")
            else:
                recommended_specialists.append("General Practitioner (Family Medicine)")

        if not recommended_tests:
            recommended_tests.append("Complete Blood Count (CBC)")

        return {
            "is_emergency": is_emergency,
            "priority": priority,
            "reasons": reasons,
            "recommended_specialists": recommended_specialists,
            "recommended_tests": recommended_tests
        }
