from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import logging
import os
from contextlib import asynccontextmanager

from .config import config
from .db.base import engine, Base
from .api.v1 import auth, whatsapp, telegram
from .file_intake.router.intake_router import router as intake_router
from .shared.exceptions import AuthenticationError, ValidationError, NotFoundError

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    datefmt=config.LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Database URL: {config.DATABASE_URL}")
    
    # Startup
    yield
    
    # Shutdown
    logger.info(f"Shutting down {config.APP_NAME}")

# Create FastAPI app
app = FastAPI(
    title=config.PROJECT_NAME,
    description="Recruitment Platform with OTP-only authentication and social login integration",
    version=config.APP_VERSION,
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=config.CORS_ALLOW_CREDENTIALS,
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=config.ALLOWED_HOSTS if config.ALLOWED_HOSTS != ["*"] else None
)

# Add HTTPS redirect middleware (for production)
if config.ENVIRONMENT == "production" and config.DEBUG == False:
    app.add_middleware(HTTPSRedirectMiddleware)

# Include API routers
app.include_router(auth.router, prefix=config.API_V1_STR)
app.include_router(whatsapp.router, prefix=config.API_V1_STR)
app.include_router(telegram.router, prefix=config.API_V1_STR)
app.include_router(intake_router, prefix=config.API_V1_STR)

# Exception handlers
@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc), "error_code": "AUTHENTICATION_ERROR"}
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "error_code": "VALIDATION_ERROR"}
    )

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "error_code": "NOT_FOUND"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with application info"""
    return {
        "message": f"Welcome to {config.PROJECT_NAME}",
        "version": config.APP_VERSION,
        "environment": config.ENVIRONMENT,
        "docs_url": "/docs" if config.DEBUG else None,
        "api_version": config.API_V1_STR
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "version": config.APP_VERSION,
            "environment": config.ENVIRONMENT,
            "database": "connected",
            "timestamp": "2025-01-01T00:00:00Z"  # Replace with actual timestamp
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": "disconnected"
        }

# API info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": config.PROJECT_NAME,
        "version": config.APP_VERSION,
        "description": "Recruitment Platform API",
        "authentication": {
            "type": "JWT",
            "otp_required": True,
            "social_login": ["whatsapp", "telegram"]
        },
        "endpoints": {
            "auth": {
                "login": "POST /api/v1/auth/login",
                "verify_otp": "POST /api/v1/auth/verify-otp",
                "refresh_token": "POST /api/v1/auth/refresh-token",
                "me": "GET /api/v1/auth/me",
                "logout": "POST /api/v1/auth/logout"
            },
            "whatsapp": {
                "webhook": "POST /api/v1/whatsapp/webhook",
                "verify": "GET /api/v1/whatsapp/webhook"
            },
            "telegram": {
                "webhook": "POST /api/v1/telegram/webhook"
            },
            "file_intake": {
                "initiate_upload": "POST /api/v1/intake/initiate-upload",
                "complete_upload": "POST /api/v1/intake/complete-upload",
                "upload_to_server": "POST /api/v1/intake/upload-to-server"
            }
        }
    }

# Rate limiting middleware (simple implementation)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting middleware"""
    if not config.RATE_LIMIT_ENABLED:
        return await call_next(request)
    
    # In production, use Redis for proper rate limiting
    # For now, just log the request
    client_ip = request.client.host
    logger.info(f"Request from {client_ip}: {request.method} {request.url}")
    
    response = await call_next(request)
    return response

# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Request logging middleware"""
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    logger.info(f"Response: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )