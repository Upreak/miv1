"""
User Repository
Handles database operations for User model.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from backend_app.db.connection import Base
from backend_app.models.users import User


class UserRepository:
    """Repository for User model operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def create(self, user_data: dict) -> User:
        """Create a new user"""
        try:
            user = User(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise e
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_login=datetime.utcnow())
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def update_last_active(self, user_id: str) -> bool:
        """Update user's last active timestamp"""
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_active=datetime.utcnow())
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def update_status(self, user_id: str, status: str) -> bool:
        """Update user status"""
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(status=status)
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def update_verification_status(self, user_id: str, is_verified: bool) -> bool:
        """Update user verification status"""
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(is_verified=is_verified)
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        try:
            result = await self.db.execute(
                select(User)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception:
            return []
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        try:
            user = await self.get_by_id(user_id)
            if user:
                await self.db.delete(user)
                await self.db.commit()
                return True
            return False
        except Exception:
            await self.db.rollback()
            return False