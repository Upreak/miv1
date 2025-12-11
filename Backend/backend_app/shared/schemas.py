from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import datetime

# Authentication Schemas
class LoginRequest(BaseModel):
    phone: constr(strip_whitespace=True, min_length=10, max_length=15)
    
    @validator('phone')
    def validate_phone(cls, v):
        # Remove any non-digit characters
        digits_only = ''.join(c for c in v if c.isdigit())
        if len(digits_only) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return digits_only

class LoginResponse(BaseModel):
    message: str
    phone: str
    otp_code: Optional[str] = None  # Remove in production

class VerifyOTPRequest(BaseModel):
    phone: constr(strip_whitespace=True, min_length=10, max_length=15)
    otp_code: constr(strip_whitespace=True, min_length=4, max_length=6)
    
    @validator('phone')
    def validate_phone(cls, v):
        digits_only = ''.join(c for c in v if c.isdigit())
        if len(digits_only) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return digits_only
    
    @validator('otp_code')
    def validate_otp(cls, v):
        # OTP should be digits only
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        return v

class VerifyOTPResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: 'UserResponse'

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# User Schemas
class UserResponse(BaseModel):
    id: str
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    telegram_id: Optional[str] = None
    role: str
    full_name: Optional[str] = None
    is_verified: bool
    status: str
    created_at: datetime
    last_login: Optional[datetime] = None
    last_active: Optional[datetime] = None

class UserCreateRequest(BaseModel):
    phone: constr(strip_whitespace=True, min_length=10, max_length=15)
    role: str = "CANDIDATE"
    full_name: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        digits_only = ''.join(c for c in v if c.isdigit())
        if len(digits_only) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return digits_only

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

# WhatsApp Webhook Schemas
class WhatsAppMessage(BaseModel):
    from_number: str
    text: Optional[str] = None
    type: str = "text"

class WhatsAppWebhook(BaseModel):
    object: str
        # "whatsapp_business_account"
    entry: list[dict]
        # Each entry contains changes

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None

class TelegramMessage(BaseModel):
    message_id: int
    from_user: dict
    chat: dict
    text: Optional[str] = None
    date: int

# Common Response Schemas
class SuccessResponse(BaseModel):
    ok: bool = True
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    ok: bool = False
    message: str
    error_code: Optional[int] = None

# Pagination Schemas
class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100
    max_limit: int = 1000

class PaginatedResponse(BaseModel):
    items: list
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool

# Health Check Schemas
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str

# Rate Limiting Schemas
class RateLimitResponse(BaseModel):
    remaining: int
    reset: int
    limit: int

# OTP Schemas
class OTPRequest(BaseModel):
    phone: constr(strip_whitespace=True, min_length=10, max_length=15)
    
    @validator('phone')
    def validate_phone(cls, v):
        digits_only = ''.join(c for c in v if c.isdigit())
        if len(digits_only) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return digits_only

class OTPVerifyRequest(BaseModel):
    phone: constr(strip_whitespace=True, min_length=10, max_length=15)
    otp_code: constr(strip_whitespace=True, min_length=4, max_length=6)
    
    @validator('phone')
    def validate_phone(cls, v):
        digits_only = ''.join(c for c in v if c.isdigit())
        if len(digits_only) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return digits_only
    
    @validator('otp_code')
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        return v

# Update forward references
UserResponse.model_rebuild()
# Candidate Profile Schemas
class CandidateProfileCreate(BaseModel):
    candidate_id: int
    personal_info: dict
    work_experience: list = []
    education: list = []
    skills: list = []
    certifications: list = []
    languages: list = []
    projects: list = []
    achievements: list = []
    metadata: dict = {}
    source: str = 'manual'

class CandidateProfileUpdate(BaseModel):
    personal_info: Optional[dict] = None
    work_experience: Optional[list] = None
    education: Optional[list] = None
    skills: Optional[list] = None
    certifications: Optional[list] = None
    languages: Optional[list] = None
    projects: Optional[list] = None
    achievements: Optional[list] = None
    metadata: Optional[dict] = None

