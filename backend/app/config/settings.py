import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database - MongoDB Atlas
    MONGODB_URL: str
    DATABASE_NAME: str = "fintech_advisor"
    
    # Clerk Configuration
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str
    CLERK_DOMAIN: str = "civil-spaniel-38.clerk.accounts.dev"
    
    # LLM/AI Configuration
    GROQ_API_KEY: str
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    llm_model: str = "llama-3.3-70b-versatile"
    
    # Sarvam AI Voice Configuration (FIXED - Made Optional)
    SARVAM_API_KEY: Optional[str] = None
    SARVAM_DEFAULT_LANGUAGE: str = "hi"
    SARVAM_TTS_SPEAKER: str = "meera"
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    APP_NAME: str = "Fintech Advisor"
    
    # Security
    SECRET_KEY: str = "test-secret-key-change-in-production"
    JWT_ALGORITHM: str = "RS256"
    
    # CORS - Updated with more origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:5174",
    ]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# Debug print for CORS (remove in production)
if settings.DEBUG:
    print(f"🌐 CORS Origins configured: {settings.CORS_ORIGINS}")
    if settings.SARVAM_API_KEY:
        print(f"🎤 Sarvam AI Voice enabled: True")
    else:
        print(f"⚠️  Sarvam AI Voice disabled: No API key found")