from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from ..db.base import get_db
from ..models.users import User
from ..repositories.user_repo import UserRepository
from ..security.otp_service import OTPService
from ..security.token_manager import TokenManager
from ..shared.schemas import (
    LoginRequest, LoginResponse, 
    VerifyOTPRequest, VerifyOTPResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    UserResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# Initialize services
token_manager = TokenManager()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        user_id = token_manager.get_user_id_from_token(token)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user with phone number and send OTP
    """
    try:
        user_repo = UserRepository(db)
        otp_service = OTPService(user_repo)
        
        # Get or create user
        user = user_repo.get_by_phone_or_create(request.phone)
        
        # Send OTP
        otp_code = otp_service.send_otp(user, send_via_sms=False)  # For demo, don't actually send SMS
        
        logger.info(f"Login initiated for phone {request.phone}")
        
        return LoginResponse(
            message=f"OTP sent to {request.phone}",
            phone=request.phone,
            otp_code=otp_code  # In production, remove this line for security
        )
        
    except Exception as e:
        logger.error(f"Login error for {request.phone}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and generate access token
    """
    try:
        user_repo = UserRepository(db)
        otp_service = OTPService(user_repo)
        
        # Get user
        user = user_repo.get_by_phone(request.phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify OTP
        if not otp_service.verify_otp(user, request.otp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Mark user as verified if not already
        if not user.is_verified:
            user = user_repo.set_verified(user)
        
        # Update last login
        user = user_repo.update_last_login(user)
        
        # Generate tokens
        tokens = token_manager.create_tokens_for_user(user.id, user.role)
        
        logger.info(f"OTP verified successfully for {request.phone}")
        
        return VerifyOTPResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=UserResponse(
                id=user.id,
                phone=user.phone,
                whatsapp_number=user.whatsapp_number,
                telegram_id=user.telegram_id,
                role=user.role,
                full_name=user.full_name,
                is_verified=user.is_verified,
                status=user.status,
                created_at=user.created_at,
                last_login=user.last_login
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP verification error for {request.phone}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/refresh-token", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        # Verify refresh token
        if not token_manager.is_refresh_token(request.refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        payload = token_manager.verify_token(request.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        role = payload.get("role")
        
        # Get user
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Generate new tokens
        tokens = token_manager.create_tokens_for_user(user.id, user.role)
        
        logger.info(f"Token refreshed for user {user_id}")
        
        return RefreshTokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    try:
        # Update last active timestamp
        user_repo = UserRepository(current_user)
        user_repo.update_last_active(current_user)
        
        return UserResponse(
            id=current_user.id,
            phone=current_user.phone,
            whatsapp_number=current_user.whatsapp_number,
            telegram_id=current_user.telegram_id,
            role=current_user.role,
            full_name=current_user.full_name,
            is_verified=current_user.is_verified,
            status=current_user.status,
            created_at=current_user.created_at,
            last_login=current_user.last_login
        )
        
    except Exception as e:
        logger.error(f"Error getting current user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (invalidate token)
    """
    try:
        # In production, you might want to add the token to a blacklist
        logger.info(f"User {current_user.id} logged out")
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )