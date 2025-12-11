"""
Authentication Service
Handles user authentication, registration, and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend_app.config_settings import settings
from backend_app.db.connection import get_db
from backend_app.models.users import User
from backend_app.repositories.user_repo import UserRepository


class AuthService:
    """Authentication service for handling user auth operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def signup(
        self, 
        email: str, 
        password: str, 
        role: str, 
        full_name: str
    ) -> User:
        """Create a new user account"""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "full_name": full_name,
            "status": "Active",
            "is_verified": False,
            "created_at": datetime.utcnow()
        }
        
        user = await self.user_repo.create(user_data)
        return user
    
    async def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return JWT tokens"""
        # Get user by email
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        
        # Check if user is active
        if user.status != "Active":
            return None
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            return None
        
        # Generate tokens
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)
        
        # Update last login
        await self.user_repo.update_last_login(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
            "role": user.role,
            "full_name": user.full_name
        }
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
        try:
            # Decode refresh token
            payload = jwt.decode(
                refresh_token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Get user from database
            user = await self.user_repo.get_by_id(user_id)
            if not user or user.status != "Active":
                return None
            
            # Generate new tokens
            access_token = self._create_access_token(user)
            refresh_token = self._create_refresh_token(user)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user.id,
                "role": user.role,
                "full_name": user.full_name
            }
            
        except jwt.PyJWTError:
            return None
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
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
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise Exception("User not found")
            
            if user.status != "Active":
                raise Exception("User account is not active")
            
            return user
            
        except jwt.PyJWTError:
            raise Exception("Invalid token")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": expire,
            "type": "access"
        }
        
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def _create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "exp": expire,
            "type": "refresh"
        }
        
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)