from fastapi import HTTPException
from typing import Optional, Dict, Any

class BaseException(Exception):
    """Base exception class for all custom exceptions"""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(BaseException):
    """Authentication related errors"""
    def __init__(self, message: str, error_code: str = "AUTHENTICATION_ERROR"):
        super().__init__(message, error_code)

class AuthorizationError(BaseException):
    """Authorization related errors"""
    def __init__(self, message: str, error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(message, error_code)

class ValidationError(BaseException):
    """Validation related errors"""
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, error_code)

class NotFoundError(BaseException):
    """Resource not found errors"""
    def __init__(self, message: str, error_code: str = "NOT_FOUND"):
        super().__init__(message, error_code)

class ConflictError(BaseException):
    """Resource conflict errors"""
    def __init__(self, message: str, error_code: str = "CONFLICT"):
        super().__init__(message, error_code)

class RateLimitError(BaseException):
    """Rate limiting errors"""
    def __init__(self, message: str, error_code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(message, error_code)

class ExternalServiceError(BaseException):
    """External service integration errors"""
    def __init__(self, message: str, service: str, error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(message, error_code)
        self.service = service

class DatabaseError(BaseException):
    """Database operation errors"""
    def __init__(self, message: str, error_code: str = "DATABASE_ERROR"):
        super().__init__(message, error_code)

class ConfigurationError(BaseException):
    """Configuration related errors"""
    def __init__(self, message: str, error_code: str = "CONFIGURATION_ERROR"):
        super().__init__(message, error_code)

class OTPError(BaseException):
    """OTP related errors"""
    def __init__(self, message: str, error_code: str = "OTP_ERROR"):
        super().__init__(message, error_code)

class WhatsAppError(BaseException):
    """WhatsApp integration errors"""
    def __init__(self, message: str, error_code: str = "WHATSAPP_ERROR"):
        super().__init__(message, error_code)

class TelegramError(BaseException):
    """Telegram integration errors"""
    def __init__(self, message: str, error_code: str = "TELEGRAM_ERROR"):
        super().__init__(message, error_code)

class FileProcessingError(BaseException):
    """File processing errors"""
    def __init__(self, message: str, error_code: str = "FILE_PROCESSING_ERROR"):
        super().__init__(message, error_code)

class SecurityError(BaseException):
    """Security related errors"""
    def __init__(self, message: str, error_code: str = "SECURITY_ERROR"):
        super().__init__(message, error_code)

class BusinessLogicError(BaseException):
    """Business logic errors"""
    def __init__(self, message: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(message, error_code)

class SystemError(BaseException):
    """System level errors"""
    def __init__(self, message: str, error_code: str = "SYSTEM_ERROR"):
        super().__init__(message, error_code)

# HTTP exception helpers
def create_http_exception(status_code: int, message: str, error_code: str = None) -> HTTPException:
    """Create HTTP exception with consistent format"""
    detail = {"message": message}
    if error_code:
        detail["error_code"] = error_code
    
    return HTTPException(status_code=status_code, detail=detail)

# Common HTTP exceptions
def unauthorized(message: str = "Authentication required", error_code: str = "UNAUTHORIZED") -> HTTPException:
    """Create 401 Unauthorized exception"""
    return create_http_exception(401, message, error_code)

def forbidden(message: str = "Access denied", error_code: str = "FORBIDDEN") -> HTTPException:
    """Create 403 Forbidden exception"""
    return create_http_exception(403, message, error_code)

def not_found(message: str = "Resource not found", error_code: str = "NOT_FOUND") -> HTTPException:
    """Create 404 Not Found exception"""
    return create_http_exception(404, message, error_code)

def bad_request(message: str = "Bad request", error_code: str = "BAD_REQUEST") -> HTTPException:
    """Create 400 Bad Request exception"""
    return create_http_exception(400, message, error_code)

def validation_error(message: str = "Validation error", error_code: str = "VALIDATION_ERROR") -> HTTPException:
    """Create 422 Validation Error exception"""
    return create_http_exception(422, message, error_code)

def conflict(message: str = "Resource conflict", error_code: str = "CONFLICT") -> HTTPException:
    """Create 409 Conflict exception"""
    return create_http_exception(409, message, error_code)

def too_many_requests(message: str = "Too many requests", error_code: str = "RATE_LIMIT_EXCEEDED") -> HTTPException:
    """Create 429 Too Many Requests exception"""
    return create_http_exception(429, message, error_code)

def internal_server_error(message: str = "Internal server error", error_code: str = "INTERNAL_SERVER_ERROR") -> HTTPException:
    """Create 500 Internal Server Error exception"""
    return create_http_exception(500, message, error_code)