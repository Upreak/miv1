"""
Authentication Service
Handles user authentication, registration, and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend_app.config_settings import settings
from backend_app.models.users import User
from backend_app.repositories.user_repo import UserRepository
from backend_app.schemas.auth import LoginResponse


class AuthService:
    """Authentication service for handling user auth operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def signup(
        self, 
        email: str, 
        password: str, 
        full_name: str, 
        role: str
    ) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise Exception("User with this email already exists")
        
        # Create new user
        user = await self.user_repo.create(
            email=email,
            password=password,
            full_name=full_name,
            role=role
        )
        
        return user
    
    async def login(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return tokens"""
        user = await self.user_repo.get_by_email(email)
        if not user or not self.user_repo.verify_password(password, user.password_hash):
            return None
        
        # Generate tokens
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)
        
        # Update last login
        await self.user_repo.update_last_login(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": str(user.id),
            "role": user.role,
            "full_name": user.full_name
        }
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(
                refresh_token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return None
            
            # Generate new tokens
            access_token = self._create_access_token(user)
            refresh_token = self._create_refresh_token(user)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": str(user.id),
                "role": user.role,
                "full_name": user.full_name
            }
        except jwt.PyJWTError:
            return None
    
    def _create_access_token(self, user: User) -> str:
        """Create access token"""
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": expire
        }
        
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def _create_refresh_token(self, user: User) -> str:
        """Create refresh token"""
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": expire
        }
        
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    async def get_current_user(
        token: str
    ) -> User:
        """Get current user from token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            user_id = payload.get("sub")
            if not user_id:
                raise Exception("Invalid token")
            
            # Get user from database
            from backend_app.db.connection import get_db
            async for db in get_db():
                user_repo = UserRepository(db)
                user = await user_repo.get_by_id(user_id)
                if not user:
                    raise Exception("User not found")
                return user
            
        except jwt.PyJWTError:
            raise Exception("Invalid token")