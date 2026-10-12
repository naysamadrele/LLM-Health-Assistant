import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test database URL before importing configurations
os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"

from backend.app.main import app
from backend.app.db.database import Base, get_db
from backend.app.db.seeds.seed_symptoms import seed_symptoms

# Create SQLite engine for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Setup: Create tables and seed data
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_symptoms()
    yield
    # Teardown: Clean up
    client.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_app.db"):
        try:
            os.remove("./test_app.db")
        except PermissionError:
            pass

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# Override get_db dependency in app
@pytest.fixture(autouse=True)
def override_db(db_session):
    def _get_db_override():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.pop(get_db, None)

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_user_flow():
    # 1. Register a new user
    reg_data = {
        "email": "testdoc@cdss.com",
        "password": "securepassword123",
        "full_name": "Dr. John Test",
        "role": "doctor"
    }
    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 201
    assert response.json()["email"] == reg_data["email"]
    assert response.json()["full_name"] == reg_data["full_name"]
    assert "id" in response.json()

    # 2. Login
    login_data = {
        "email": "testdoc@cdss.com",
        "password": "securepassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token_json = response.json()
    assert "access_token" in token_json
    assert token_json["token_type"] == "bearer"
    
    token = token_json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Read current user details
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == reg_data["email"]

    # 4. Create patient
    patient_data = {
        "name": "Jane Patient",
        "age": 45,
        "gender": "Female",
        "height": 165.0,
        "weight": 68.5
    }
    response = client.post("/api/v1/patients/", json=patient_data, headers=headers)
    assert response.status_code == 201
    patient_json = response.json()
    assert patient_json["name"] == patient_data["name"]
    patient_id = patient_json["id"]

    # 5. Get symptoms lists
    response = client.get("/api/v1/symptoms/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # Filter symptoms
    response = client.get("/api/v1/symptoms/?search=chest_pain", headers=headers)
    assert response.status_code == 200
    assert response.json()[0]["code"] == "chest_pain"

    # 6. Create assessment with red flags (EMERGENCY)
    emergency_assessment = {
        "patient_id": patient_id,
        "blood_pressure_systolic": 150,
        "blood_pressure_diastolic": 95,
        "heart_rate": 90,
        "temperature": 37.2,
        "respiratory_rate": 18,
        "oxygen_saturation": 98,
        "blood_sugar": 110,
        "symptoms": ["chest_pain", "shortness_of_breath"], # Triggers emergency
        "lifestyle": {"smoking": "former"},
        "medical_history": {"hypertension": True}
    }
    response = client.post("/api/v1/assessments/", json=emergency_assessment, headers=headers)
    assert response.status_code == 201
    assessment_json = response.json()
    assert assessment_json["priority"] == "EMERGENCY"
    assert assessment_json["is_emergency"] is True
    assert "Chest Pain & Shortness of Breath" in assessment_json["emergency_reason"]
    
    # 7. Create assessment with standard parameters (LOW)
    low_assessment = {
        "patient_id": patient_id,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "heart_rate": 72,
        "temperature": 36.6,
        "respiratory_rate": 16,
        "oxygen_saturation": 99,
        "blood_sugar": 90,
        "symptoms": ["headache"],
        "lifestyle": {"smoking": "never"},
        "medical_history": {}
    }
    response = client.post("/api/v1/assessments/", json=low_assessment, headers=headers)
    assert response.status_code == 201
    assert response.json()["priority"] == "LOW"
    assert response.json()["is_emergency"] is False
