import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.database import engine, Base
from backend.app.db.seeds.seed_symptoms import seed_symptoms
from backend.app.api import auth, patients, symptoms, assessments

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database schema and run seed scripts
try:
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
    
    # Run seeding logic
    seed_symptoms()
except Exception as e:
    logger.error(f"Error during database initialization/seeding: {e}")

# Instantiate FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Explainable Clinical Decision Support System (CDSS) for general health assessment.",
    version="1.0.0"
)

# CORS configuration to allow React frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(patients.router, prefix=f"{settings.API_V1_STR}/patients", tags=["Patients"])
app.include_router(symptoms.router, prefix=f"{settings.API_V1_STR}/symptoms", tags=["Symptoms"])
app.include_router(assessments.router, prefix=f"{settings.API_V1_STR}/assessments", tags=["Assessments"])

@app.get("/")
def health_check():
    """Health check endpoint to ensure backend is running."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
