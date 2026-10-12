import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Explainable CDSS"
    API_V1_STR: str = "/api/v1"
    
    # JWT authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "b3d906103323a7e43594b59f3d9b4bf10cbb2ffb6232777174e2d42bb24c6e9a")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # Database Settings: default to local SQLite so the app can run without external services.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cdss.db")
    
    # Vector DB (Chroma) Settings
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Ollama Settings
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3:8b-instruct-q4_K_M")

settings = Settings()
