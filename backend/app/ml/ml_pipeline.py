import os
import pickle
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

class MLPredictionPipeline:
    _models = {}
    _scalers = {}
    _features = {}
    _loaded = False

    @classmethod
    def load_artifacts(cls):
        """Lazy loads models, scalers, and feature lists from disk."""
        if cls._loaded:
            return

        artifacts_dir = "./backend/app/ml/artifacts"
        diseases = ["diabetes", "heart", "stroke", "kidney"]
        
        # Check if files exist. If not, train them first
        if not all(os.path.exists(os.path.join(artifacts_dir, f"{d}_model.pkl")) for d in diseases):
            print("ML model artifacts not found. Running training script...")
            from backend.app.ml.train_models import train_and_save_models
            train_and_save_models()

        for d in diseases:
            with open(os.path.join(artifacts_dir, f"{d}_model.pkl"), "rb") as f:
                cls._models[d] = pickle.load(f)
            with open(os.path.join(artifacts_dir, f"{d}_scaler.pkl"), "rb") as f:
                cls._scalers[d] = pickle.load(f)
            with open(os.path.join(artifacts_dir, f"{d}_features.pkl"), "rb") as f:
                cls._features[d] = pickle.load(f)
                
        cls._loaded = True
        print("ML Model pipeline artifacts loaded successfully.")

    @classmethod
    def _parse_features(cls, patient: Any, assessment: Any) -> Dict[str, float]:
        """
        Parses complex demographic, vital signs, symptoms, lifestyle, and medical history
        into a unified flat dictionary of float features.
        """
        # Calculate BMI
        height_m = patient.height / 100.0
        bmi = patient.weight / (height_m ** 2) if height_m > 0 else 24.0

        symptom_set = set(assessment.symptoms)
        lifestyle = assessment.lifestyle or {}
        med_hx = assessment.medical_history or {}

        # 1. Parse Exercise (0: none, 1: moderate, 2: active)
        exercise_str = str(lifestyle.get("exercise", "moderate")).lower()
        if "active" in exercise_str or "high" in exercise_str or "daily" in exercise_str:
            exercise = 2
        elif "none" in exercise_str or "sedentary" in exercise_str:
            exercise = 0
        else:
            exercise = 1

        # 2. Parse Smoking (0: no, 1: active)
        smoking_str = str(lifestyle.get("smoking", "never")).lower()
        smoking = 1 if ("active" in smoking_str or "yes" in smoking_str or "daily" in smoking_str or "smoker" in smoking_str) else 0

        # 3. Parse Alcohol (0: none, 1: moderate, 2: heavy)
        alcohol_str = str(lifestyle.get("alcohol", "none")).lower()
        if "heavy" in alcohol_str or "high" in alcohol_str or "frequent" in alcohol_str:
            alcohol = 2
        elif "none" in alcohol_str or "never" in alcohol_str:
            alcohol = 0
        else:
            alcohol = 1

        # Medical History indicators
        diabetes_hx = 1 if med_hx.get("diabetes") is True or str(med_hx.get("diabetes")).lower() == "true" else 0
        hypertension_hx = 1 if med_hx.get("hypertension") is True or str(med_hx.get("hypertension")).lower() == "true" else 0
        heart_disease_hx = 1 if med_hx.get("heart_disease") is True or str(med_hx.get("heart_disease")).lower() == "true" else 0
        family_history = 1 if med_hx.get("family_history") is True or str(med_hx.get("family_history")).lower() == "true" else 0

        # Symptoms
        chest_pain = 1 if "chest_pain" in symptom_set else 0
        palpitations = 1 if "palpitations" in symptom_set else 0
        flank_pain = 1 if "flank_pain" in symptom_set else 0
        anuria = 1 if "anuria" in symptom_set else 0

        return {
            "age": float(patient.age),
            "bmi": float(bmi),
            "systolic_bp": float(assessment.blood_pressure_systolic),
            "diastolic_bp": float(assessment.blood_pressure_diastolic),
            "blood_sugar": float(assessment.blood_sugar if assessment.blood_sugar is not None else 95.0),
            "heart_rate": float(assessment.heart_rate),
            "exercise": float(exercise),
            "smoking": float(smoking),
            "alcohol": float(alcohol),
            "family_history": float(family_history),
            "diabetes_hx": float(diabetes_hx),
            "hypertension_hx": float(hypertension_hx),
            "heart_disease_hx": float(heart_disease_hx),
            "chest_pain": float(chest_pain),
            "palpitations": float(palpitations),
            "flank_pain": float(flank_pain),
            "anuria": float(anuria)
        }

    @classmethod
    def predict(cls, patient: Any, assessment: Any) -> Dict[str, Tuple[float, Dict[str, Any]]]:
        """
        Runs prediction for all 4 models and returns probability and feature map.
        Returns: Dict[disease_name, (probability, feature_dict)]
        """
        cls.load_artifacts()
        
        parsed_feats = cls._parse_features(patient, assessment)
        results = {}

        # 1. Predict Diabetes
        results["Diabetes"] = cls._predict_single(
            disease_key="diabetes",
            numeric_cols=["age", "bmi", "systolic_bp", "diastolic_bp", "blood_sugar"],
            parsed_feats=parsed_feats
        )

        # 2. Predict Heart Disease
        results["Heart Disease"] = cls._predict_single(
            disease_key="heart",
            numeric_cols=["age", "bmi", "systolic_bp", "heart_rate"],
            parsed_feats=parsed_feats
        )

        # 3. Predict Stroke Risk
        results["Stroke Risk"] = cls._predict_single(
            disease_key="stroke",
            numeric_cols=["age", "systolic_bp", "heart_rate"],
            parsed_feats=parsed_feats
        )

        # 4. Predict Kidney Disease
        results["Kidney Disease"] = cls._predict_single(
            disease_key="kidney",
            numeric_cols=["age", "bmi", "systolic_bp"],
            parsed_feats=parsed_feats
        )

        return results

    @classmethod
    def _predict_single(
        cls,
        disease_key: str,
        numeric_cols: List[str],
        parsed_feats: Dict[str, float]
    ) -> Tuple[float, Dict[str, float]]:
        """Utility function to scale and predict a single disease outcome."""
        model = cls._models[disease_key]
        scaler = cls._scalers[disease_key]
        feature_names = cls._features[disease_key]

        # Construct raw row matching exact features
        raw_row = {feat: parsed_feats[feat] for feat in feature_names}
        
        # Scale only numeric columns
        df_row = pd.DataFrame([raw_row])
        df_row_scaled = df_row.copy()
        df_row_scaled[numeric_cols] = scaler.transform(df_row[numeric_cols])

        # Run model prediction
        prob = float(model.predict_proba(df_row_scaled)[0][1])
        
        # Return probability and the raw scaled feature row for SHAP calculations
        return prob, df_row_scaled.iloc[0].to_dict()
