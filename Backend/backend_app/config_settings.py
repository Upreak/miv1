"""
Application Configuration
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator, field_validator


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "AI Recruitment Backend"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    
    # Database settings
    DATABASE_URL: str = "postgresql://myuser:mysecurepwd@localhost:5432/recruitment_db"
    ASYNC_DATABASE_URL: Optional[str] = None  # Will be derived from DATABASE_URL
    DATABASE_ECHO: bool = False
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: str = "application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
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
    
    # Chatbot settings
    FRESHNESS_DAYS: int = 30
    EXPORT_TMP_PATH: str = "/data/exports"
    QUARANTINE_BASE_PATH: str = "/data/quarantine"
    WHATSAPP_OUTBOUND_WEBHOOK_URL: str = ""
    EMAIL_SENDER_SMTP_HOST: str = ""
    EMAIL_SENDER_SMTP_PORT: int = 587
    EMAIL_SENDER_SMTP_USERNAME: str = ""
    EMAIL_SENDER_SMTP_PASSWORD: str = ""
    EMAIL_SENDER_SMTP_USE_TLS: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Provider Configuration (Phase 4)
    ENABLE_PROVIDER_SYSTEM: bool = True
    PRIMARY_PROVIDER: str = "openrouter"
    SECONDARY_PROVIDER: str = "gemini"
    FALLBACK_PROVIDER: str = "groq"
    
    # Provider API Keys
    OPENROUTER_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # Provider Settings
    PROVIDER_TIMEOUT: int = 30
    PROVIDER_RETRY_ATTEMPTS: int = 3
    PROVIDER_LOAD_BALANCE: str = "round_robin"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in environment variables
    
    @field_validator('ASYNC_DATABASE_URL', mode='before')
    def set_async_database_url(cls, v, values):
        """Auto-generate async database URL from sync URL"""
        if v:
            return v
        
        # Get sync URL
        sync_url = values.data.get('DATABASE_URL')
        if sync_url:
            # Replace postgresql:// with postgresql+asyncpg://
            return sync_url.replace('postgresql://', 'postgresql+asyncpg://')
        
        return "postgresql+asyncpg://myuser:mysecurepwd@localhost:5432/recruitment_db"


settings = Settings()