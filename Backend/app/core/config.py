from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Recruitment Backend"
    DEBUG: bool = False
    API_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/recruitment_db"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OTP Configuration
    OTP_LENGTH: int = 6
    OTP_EXPIRY_MINUTES: int = 5
    SEND_OTP_VIA_SMS: bool = False
    
    # WhatsApp Configuration
    WHATSAPP_VERIFY_TOKEN: str = "your-whatsapp-verify-token"
    WHATSAPP_WEBHOOK_SECRET: str = "your-whatsapp-webhook-secret"
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = "your-telegram-bot-token"
    
    # Log Level
    LOG_LEVEL: str = "INFO"
    
    # Bcrypt Rounds
    BCRYPT_ROUNDS: int = 12
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8000"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Development Configuration
    DEV_MODE: bool = True
    DEV_PHONE_NUMBER: str = "919876543210"
    DEV_OTP_CODE: str = "123456"
    
    # Environment Configuration
    ENVIRONMENT: str = "development"
    ALLOWED_HOSTS: str = "*"
    
    # Testing Configuration
    TEST_MODE: bool = True
    
    # External Services
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    
    # File Storage
    STORAGE_BUCKET: str = "recruitment-files"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    
    # Redis (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Override with environment variables if available
if os.getenv("DATABASE_URL"):
    settings.DATABASE_URL = os.getenv("DATABASE_URL")

if os.getenv("SECRET_KEY"):
    settings.SECRET_KEY = os.getenv("SECRET_KEY")

if os.getenv("ALLOWED_ORIGINS"):
    settings.ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")