"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    user_id: str
    role: str
    full_name: str


class SignupRequest(BaseModel):
    """Signup request schema"""
    email: EmailStr
    password: str
    full_name: str
    role: str  # ADMIN, RECRUITER, SALES, CANDIDATE, MANAGER


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    full_name: str
    role: str
    status: str

    class Config:
        from_attributes = True