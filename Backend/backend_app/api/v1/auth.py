"""
Authentication API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from backend_app.db.connection import get_db
from backend_app.schemas.auth import LoginRequest, LoginResponse, SignupRequest, RefreshTokenRequest
from backend_app.services.auth import AuthService
from backend_app.models.users import User
from pydantic import BaseModel

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """User login endpoint"""
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.login(request.email, request.password)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return LoginResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type="bearer",
            user_id=result["user_id"],
            role=result["role"],
            full_name=result["full_name"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/signup")
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """User signup endpoint"""
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.signup(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
        
        return {
            "message": "User created successfully",
            "user_id": user.id,
            "email": user.email
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token endpoint"""
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.refresh_token(request.refresh_token)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return LoginResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type="bearer",
            user_id=result["user_id"],
            role=result["role"],
            full_name=result["full_name"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


class CurrentUserResponse(BaseModel):
    """Response model for current user information"""
    id: str
    email: str
    full_name: str
    role: str
    status: str


@router.get("/me")
async def get_current_user(
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get current user information"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "status": current_user.status
    }