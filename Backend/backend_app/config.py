"""
Application Configuration
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "AI Recruitment Backend"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/recruitment_db"
    DATABASE_ECHO: bool = False
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # External services
    EXTERNAL_JOB_API_URL: str = "https://api.example.com/jobs"
    EXTERNAL_JOB_API_KEY: str = ""
    
    # Redis settings (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Email settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    
    # File storage
    STORAGE_TYPE: str = "local"  # local, s3
    STORAGE_PATH: str = "./uploads"
    S3_BUCKET: str = ""
    S3_REGION: str = "us-east-1"
    
    # AI/ML settings
    AI_PROVIDER: str = "openrouter"  # openrouter, gemini, groq
    AI_MODEL: str = "gpt-4o-mini"
    AI_API_KEY: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()