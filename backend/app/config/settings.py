import os
from typing import List
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
    # GROQ_API_KEY: str = "test_groq_key"
    GROQ_API_KEY: str  # Remove the = "test_groq_key" part

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    llm_model: str = "llama-3.3-70b-versatile"  # Added this field
    
    # Security
    SECRET_KEY: str = "test-secret-key-change-in-production"
    JWT_ALGORITHM: str = "RS256"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()