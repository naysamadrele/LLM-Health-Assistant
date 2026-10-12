import os
import numpy as np
import pandas as pd

def generate_diabetes_data(n_samples=2000):
    """
    Generates synthetic data for Diabetes classification.
    Features: Age, BMI, Systolic BP, Diastolic BP, Blood Sugar, Exercise, Smoking, Family History
    """
    np.random.seed(42)
    
    # Demographics & Vitals
    age = np.random.randint(18, 85, n_samples)
    bmi = np.random.normal(27, 6, n_samples)
    bmi = np.clip(bmi, 15, 50)
    systolic_bp = np.random.normal(125, 15, n_samples)
    diastolic_bp = np.random.normal(80, 10, n_samples)
    
    # Blood sugar: higher values correlate with higher age and BMI
    blood_sugar_base = np.random.normal(95, 15, n_samples)
    blood_sugar = blood_sugar_base + (bmi - 25) * 1.5 + (age - 35) * 0.4
    blood_sugar = np.clip(blood_sugar, 60, 300)
    
    # Lifestyle and medical history
    exercise = np.random.choice([0, 1, 2], n_samples, p=[0.3, 0.5, 0.2]) # 0: none, 1: moderate, 2: active
    smoking = np.random.choice([0, 1], n_samples, p=[0.6, 0.4]) # 0: never/former, 1: active
    family_history = np.random.choice([0, 1], n_samples, p=[0.7, 0.3]) # 0: no, 1: yes
    
    # Probability score logic
    log_odds = (
        -7.0 + 
        0.04 * age + 
        0.18 * (bmi - 25) + 
        0.02 * (systolic_bp - 120) + 
        0.035 * (blood_sugar - 100) + 
        1.5 * family_history +
        0.5 * smoking - 
        0.6 * exercise
    )
    
    prob = 1 / (1 + np.exp(-log_odds))
    target = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        "age": age,
        "bmi": bmi,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "blood_sugar": blood_sugar,
        "exercise": exercise,
        "smoking": smoking,
        "family_history": family_history,
        "outcome": target
    })
    
    return df

def generate_heart_disease_data(n_samples=2000):
    """
    Generates synthetic data for Heart Disease classification.
    Features: Age, BMI, Systolic BP, Heart Rate, Smoking, Chest Pain, Palpitations, Hypertension History
    """
    np.random.seed(43)
    
    age = np.random.randint(25, 90, n_samples)
    bmi = np.random.normal(26, 5, n_samples)
    systolic_bp = np.random.normal(128, 18, n_samples)
    heart_rate = np.random.normal(75, 12, n_samples)
    
    smoking = np.random.choice([0, 1], n_samples, p=[0.55, 0.45])
    chest_pain = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    palpitations = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    hypertension_hx = np.random.choice([0, 1], n_samples, p=[0.65, 0.35])
    
    log_odds = (
        -6.5 + 
        0.05 * age + 
        0.12 * (bmi - 25) + 
        0.03 * (systolic_bp - 120) + 
        0.02 * (heart_rate - 70) + 
        1.2 * smoking + 
        2.5 * chest_pain + 
        0.8 * palpitations + 
        1.4 * hypertension_hx
    )
    
    prob = 1 / (1 + np.exp(-log_odds))
    target = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        "age": age,
        "bmi": bmi,
        "systolic_bp": systolic_bp,
        "heart_rate": heart_rate,
        "smoking": smoking,
        "chest_pain": chest_pain,
        "palpitations": palpitations,
        "hypertension_hx": hypertension_hx,
        "outcome": target
    })
    
    return df

def generate_stroke_data(n_samples=2000):
    """
    Generates synthetic data for Stroke Risk classification.
    Features: Age, Systolic BP, Heart Rate, Smoking, Alcohol, Diabetes History, Heart Disease History
    """
    np.random.seed(44)
    
    age = np.random.randint(30, 95, n_samples)
    systolic_bp = np.random.normal(132, 20, n_samples)
    heart_rate = np.random.normal(76, 15, n_samples)
    
    smoking = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    alcohol = np.random.choice([0, 1, 2], n_samples, p=[0.5, 0.4, 0.1]) # none, moderate, heavy
    diabetes_hx = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    heart_disease_hx = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    
    log_odds = (
        -8.0 + 
        0.07 * age + 
        0.04 * (systolic_bp - 120) + 
        0.015 * (heart_rate - 70) + 
        1.1 * smoking + 
        0.4 * alcohol + 
        1.3 * diabetes_hx + 
        1.8 * heart_disease_hx
    )
    
    prob = 1 / (1 + np.exp(-log_odds))
    target = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        "age": age,
        "systolic_bp": systolic_bp,
        "heart_rate": heart_rate,
        "smoking": smoking,
        "alcohol": alcohol,
        "diabetes_hx": diabetes_hx,
        "heart_disease_hx": heart_disease_hx,
        "outcome": target
    })
    
    return df

def generate_kidney_disease_data(n_samples=2000):
    """
    Generates synthetic data for Chronic Kidney Disease (CKD).
    Features: Age, BMI, Systolic BP, Diabetes History, Hypertension History, Flank Pain, Anuria
    """
    np.random.seed(45)
    
    age = np.random.randint(20, 85, n_samples)
    bmi = np.random.normal(26.5, 5.5, n_samples)
    systolic_bp = np.random.normal(130, 16, n_samples)
    
    diabetes_hx = np.random.choice([0, 1], n_samples, p=[0.75, 0.25])
    hypertension_hx = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    flank_pain = np.random.choice([0, 1], n_samples, p=[0.92, 0.08])
    anuria = np.random.choice([0, 1], n_samples, p=[0.98, 0.02])
    
    log_odds = (
        -7.5 + 
        0.03 * age + 
        0.08 * (bmi - 25) + 
        0.025 * (systolic_bp - 120) + 
        1.5 * diabetes_hx + 
        1.6 * hypertension_hx + 
        2.2 * flank_pain + 
        4.0 * anuria
    )
    
    prob = 1 / (1 + np.exp(-log_odds))
    target = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        "age": age,
        "bmi": bmi,
        "systolic_bp": systolic_bp,
        "diabetes_hx": diabetes_hx,
        "hypertension_hx": hypertension_hx,
        "flank_pain": flank_pain,
        "anuria": anuria,
        "outcome": target
    })
    
    return df

def generate_all_data():
    os.makedirs("./backend/app/ml/data", exist_ok=True)
    
    diabetes_df = generate_diabetes_data()
    diabetes_df.to_csv("./backend/app/ml/data/diabetes_data.csv", index=False)
    print("Generated diabetes data.")
    
    heart_df = generate_heart_disease_data()
    heart_df.to_csv("./backend/app/ml/data/heart_data.csv", index=False)
    print("Generated heart disease data.")
    
    stroke_df = generate_stroke_data()
    stroke_df.to_csv("./backend/app/ml/data/stroke_data.csv", index=False)
    print("Generated stroke risk data.")
    
    kidney_df = generate_kidney_disease_data()
    kidney_df.to_csv("./backend/app/ml/data/kidney_data.csv", index=False)
    print("Generated kidney disease data.")

if __name__ == "__main__":
    generate_all_data()
