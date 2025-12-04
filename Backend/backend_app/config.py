import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./recruitment_app.db")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

# OTP Configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
SEND_OTP_VIA_SMS = os.getenv("SEND_OTP_VIA_SMS", "false").lower() == "true"

# WhatsApp Configuration
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "your_verify_token_here")
WHATSAPP_WEBHOOK_SECRET = os.getenv("WHATSAPP_WEBHOOK_SECRET", "your_webhook_secret_here")
WHATSAPP_BUSINESS_PHONE_NUMBER_ID = os.getenv("WHATSAPP_BUSINESS_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")

# SMS Configuration (for production)
SMS_PROVIDER = os.getenv("SMS_PROVIDER", "twilio")  # twilio, aws_sns, etc.
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Email Configuration (optional fallback)
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Application Configuration
APP_NAME = "Recruitment Platform"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Security Configuration
BCRYPT_ROUNDS = 12
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["*"]

# API Configuration
API_V1_STR = "/api/v1"
PROJECT_NAME = "Recruitment Platform"

# File Upload Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_FILE_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/jpeg",
    "image/png"
]

# Redis Configuration (for caching and rate limiting)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"

# Logging Configuration
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Environment Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# Database Configuration for different environments
if ENVIRONMENT == "production":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/recruitment_db")
elif ENVIRONMENT == "development":
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./recruitment_dev.db")

# Configuration validation
def validate_config():
    """Validate configuration settings"""
    required_vars = [
        "JWT_SECRET_KEY",
        "WHATSAPP_VERIFY_TOKEN",
        "WHATSAPP_WEBHOOK_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Validate phone number format for WhatsApp
    if WHATSAPP_BUSINESS_PHONE_NUMBER_ID and not WHATSAPP_BUSINESS_PHONE_NUMBER_ID.isdigit():
        raise ValueError("WhatsApp Business Phone Number ID must be numeric")
    
    # Validate Telegram bot token format
    if TELEGRAM_BOT_TOKEN and not TELEGRAM_BOT_TOKEN.startswith("bot"):
        raise ValueError("Telegram Bot Token must start with 'bot'")
    
    # Validate SMS provider configuration
    if SMS_PROVIDER == "twilio":
        required_sms_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]
        for var in required_sms_vars:
            if not os.getenv(var):
                missing_vars.append(var)
    
    return True

# Validate configuration on import
try:
    validate_config()
except ValueError as e:
    print(f"Configuration validation error: {e}")
    print("Please check your environment variables or .env file")
    raise

# Configuration class for easy access
class Config:
    def __init__(self):
        self.DATABASE_URL = DATABASE_URL
        self.JWT_SECRET_KEY = JWT_SECRET_KEY
        self.JWT_ALGORITHM = JWT_ALGORITHM
        self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.JWT_REFRESH_TOKEN_EXPIRE_DAYS = JWT_REFRESH_TOKEN_EXPIRE_DAYS
        self.OTP_LENGTH = OTP_LENGTH
        self.OTP_EXPIRY_MINUTES = OTP_EXPIRY_MINUTES
        self.SEND_OTP_VIA_SMS = SEND_OTP_VIA_SMS
        self.WHATSAPP_VERIFY_TOKEN = WHATSAPP_VERIFY_TOKEN
        self.WHATSAPP_WEBHOOK_SECRET = WHATSAPP_WEBHOOK_SECRET
        self.WHATSAPP_BUSINESS_PHONE_NUMBER_ID = WHATSAPP_BUSINESS_PHONE_NUMBER_ID
        self.WHATSAPP_ACCESS_TOKEN = WHATSAPP_ACCESS_TOKEN
        self.TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
        self.TELEGRAM_WEBHOOK_URL = TELEGRAM_WEBHOOK_URL
        self.SMS_PROVIDER = SMS_PROVIDER
        self.TWILIO_ACCOUNT_SID = TWILIO_ACCOUNT_SID
        self.TWILIO_AUTH_TOKEN = TWILIO_AUTH_TOKEN
        self.TWILIO_PHONE_NUMBER = TWILIO_PHONE_NUMBER
        self.EMAIL_ENABLED = EMAIL_ENABLED
        self.SMTP_SERVER = SMTP_SERVER
        self.SMTP_PORT = SMTP_PORT
        self.SMTP_USERNAME = SMTP_USERNAME
        self.SMTP_PASSWORD = SMTP_PASSWORD
        self.APP_NAME = APP_NAME
        self.APP_VERSION = APP_VERSION
        self.DEBUG = DEBUG
        self.LOG_LEVEL = LOG_LEVEL
        self.BCRYPT_ROUNDS = BCRYPT_ROUNDS
        self.RATE_LIMIT_ENABLED = RATE_LIMIT_ENABLED
        self.RATE_LIMIT_REQUESTS = RATE_LIMIT_REQUESTS
        self.RATE_LIMIT_WINDOW = RATE_LIMIT_WINDOW
        self.CORS_ORIGINS = CORS_ORIGINS
        self.CORS_ALLOW_CREDENTIALS = CORS_ALLOW_CREDENTIALS
        self.CORS_ALLOW_METHODS = CORS_ALLOW_METHODS
        self.CORS_ALLOW_HEADERS = CORS_ALLOW_HEADERS
        self.API_V1_STR = API_V1_STR
        self.PROJECT_NAME = PROJECT_NAME
        self.UPLOAD_DIR = UPLOAD_DIR
        self.MAX_FILE_SIZE = MAX_FILE_SIZE
        self.ALLOWED_FILE_TYPES = ALLOWED_FILE_TYPES
        self.REDIS_URL = REDIS_URL
        self.REDIS_ENABLED = REDIS_ENABLED
        self.LOG_FILE = LOG_FILE
        self.LOG_FORMAT = LOG_FORMAT
        self.LOG_DATE_FORMAT = LOG_DATE_FORMAT
        self.ENVIRONMENT = ENVIRONMENT
        self.ALLOWED_HOSTS = ALLOWED_HOSTS

# Global configuration instance
config = Config()