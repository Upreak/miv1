from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.schemas.users import UserCreate, UserUpdate, UserResponse, UserLogin, UserVerify, UserLogout
from app.models.users import User
from app.core.config import settings
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt

router = APIRouter()

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=dict)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """User login endpoint"""
    user = db.query(User).filter(User.email == user_login.email).first()
    
    if not user or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    user.last_login = datetime.utcnow()
    user.last_active = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.post("/signup", response_model=UserResponse)
async def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    """User signup endpoint"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_create.password)
    user = User(
        id=uuid.uuid4(),
        email=user_create.email,
        password_hash=hashed_password,
        full_name=user_create.full_name,
        role=user_create.role,
        status="Active",
        is_verified=False,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/verify", response_model=dict)
async def verify_user(user_verify: UserVerify, db: Session = Depends(get_db)):
    """User verification endpoint"""
    user = db.query(User).filter(User.email == user_verify.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # In a real implementation, you would verify the OTP
    # For now, we'll just mark the user as verified
    user.is_verified = True
    user.last_active = datetime.utcnow()
    db.commit()
    
    return {
        "message": "User verified successfully",
        "user_id": str(user.id)
    }

@router.post("/logout", response_model=dict)
async def logout(user_logout: UserLogout, db: Session = Depends(get_db)):
    """User logout endpoint"""
    user = db.query(User).filter(User.id == uuid.UUID(user_logout.user_id)).first()
    
    if user:
        user.last_active = datetime.utcnow()
        db.commit()
    
    return {"message": "Logged out successfully"}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user"""
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    user.last_active = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users