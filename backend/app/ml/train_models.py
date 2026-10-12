import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

from backend.app.ml.generate_data import generate_all_data

def train_and_save_models():
    # Make sure directories exist
    os.makedirs("./backend/app/ml/data", exist_ok=True)
    os.makedirs("./backend/app/ml/artifacts", exist_ok=True)

    # 1. Generate data if not exists
    data_files = ["diabetes_data.csv", "heart_data.csv", "stroke_data.csv", "kidney_data.csv"]
    if not all(os.path.exists(os.path.join("./backend/app/ml/data", f)) for f in data_files):
        print("Dataset files missing. Triggering generation script...")
        generate_all_data()

    # ----------------------------------------------------
    # 2. Train Diabetes Classifier (XGBoost)
    # ----------------------------------------------------
    print("\n--- Training Diabetes Classifier ---")
    df = pd.read_csv("./backend/app/ml/data/diabetes_data.csv")
    X = df.drop(columns=["outcome"])
    y = df["outcome"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    # scale age, bmi, systolic_bp, diastolic_bp, blood_sugar (indices 0 to 4)
    # Fit scaler on training set
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    numeric_cols = ["age", "bmi", "systolic_bp", "diastolic_bp", "blood_sugar"]
    X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])
    
    model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    preds = model.predict(X_test_scaled)
    print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
    print(f"F1-Score: {f1_score(y_test, preds):.4f}")
    
    with open("./backend/app/ml/artifacts/diabetes_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("./backend/app/ml/artifacts/diabetes_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("./backend/app/ml/artifacts/diabetes_features.pkl", "wb") as f:
        pickle.dump(list(X.columns), f)

    # ----------------------------------------------------
    # 3. Train Heart Disease Classifier (XGBoost)
    # ----------------------------------------------------
    print("\n--- Training Heart Disease Classifier ---")
    df = pd.read_csv("./backend/app/ml/data/heart_data.csv")
    X = df.drop(columns=["outcome"])
    y = df["outcome"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    numeric_cols = ["age", "bmi", "systolic_bp", "heart_rate"]
    X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])
    
    model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    preds = model.predict(X_test_scaled)
    print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
    print(f"F1-Score: {f1_score(y_test, preds):.4f}")
    
    with open("./backend/app/ml/artifacts/heart_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("./backend/app/ml/artifacts/heart_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("./backend/app/ml/artifacts/heart_features.pkl", "wb") as f:
        pickle.dump(list(X.columns), f)

    # ----------------------------------------------------
    # 4. Train Stroke Risk Classifier (Random Forest)
    # ----------------------------------------------------
    print("\n--- Training Stroke Risk Classifier ---")
    df = pd.read_csv("./backend/app/ml/data/stroke_data.csv")
    X = df.drop(columns=["outcome"])
    y = df["outcome"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    numeric_cols = ["age", "systolic_bp", "heart_rate"]
    X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])
    
    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    preds = model.predict(X_test_scaled)
    print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
    print(f"F1-Score: {f1_score(y_test, preds):.4f}")
    
    with open("./backend/app/ml/artifacts/stroke_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("./backend/app/ml/artifacts/stroke_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("./backend/app/ml/artifacts/stroke_features.pkl", "wb") as f:
        pickle.dump(list(X.columns), f)

    # ----------------------------------------------------
    # 5. Train Kidney Disease Classifier (Random Forest)
    # ----------------------------------------------------
    print("\n--- Training Kidney Disease Classifier ---")
    df = pd.read_csv("./backend/app/ml/data/kidney_data.csv")
    X = df.drop(columns=["outcome"])
    y = df["outcome"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    numeric_cols = ["age", "bmi", "systolic_bp"]
    X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])
    
    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    preds = model.predict(X_test_scaled)
    print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
    print(f"F1-Score: {f1_score(y_test, preds):.4f}")
    
    with open("./backend/app/ml/artifacts/kidney_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("./backend/app/ml/artifacts/kidney_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("./backend/app/ml/artifacts/kidney_features.pkl", "wb") as f:
        pickle.dump(list(X.columns), f)
        
    print("\nAll models trained and saved successfully.")

if __name__ == "__main__":
    train_and_save_models()
