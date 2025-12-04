from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.users import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            return None
    
    def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number"""
        try:
            return self.db.query(User).filter(User.phone == phone).first()
        except Exception as e:
            logger.error(f"Error getting user by phone {phone}: {str(e)}")
            return None
    
    def get_by_whatsapp(self, whatsapp_number: str) -> Optional[User]:
        """Get user by WhatsApp number"""
        try:
            return self.db.query(User).filter(User.whatsapp_number == whatsapp_number).first()
        except Exception as e:
            logger.error(f"Error getting user by WhatsApp {whatsapp_number}: {str(e)}")
            return None
    
    def get_by_telegram(self, telegram_id: str) -> Optional[User]:
        """Get user by Telegram ID"""
        try:
            return self.db.query(User).filter(User.telegram_id == telegram_id).first()
        except Exception as e:
            logger.error(f"Error getting user by Telegram ID {telegram_id}: {str(e)}")
            return None
    
    def get_by_phone_or_create(self, phone: str, role: str = "CANDIDATE") -> User:
        """Get user by phone or create new user"""
        try:
            user = self.get_by_phone(phone)
            if user:
                return user
            
            # Create new user
            user = User(
                phone=phone,
                role=role,
                is_verified=False,
                status="Active"
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created new user with phone {phone}")
            return user
            
        except Exception as e:
            logger.error(f"Error getting or creating user with phone {phone}: {str(e)}")
            self.db.rollback()
            raise
    
    def get_by_telegram_or_create(self, telegram_id: str, role: str = "CANDIDATE") -> User:
        """Get user by Telegram ID or create new user"""
        try:
            user = self.get_by_telegram(telegram_id)
            if user:
                return user
            
            # Create new user with Telegram ID
            user = User(
                telegram_id=telegram_id,
                role=role,
                is_verified=True,  # Telegram users are automatically verified
                status="Active"
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created new user with Telegram ID {telegram_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error getting or creating user with Telegram ID {telegram_id}: {str(e)}")
            self.db.rollback()
            raise
    
    def get_by_whatsapp_or_create(self, whatsapp_number: str, role: str = "CANDIDATE") -> User:
        """Get user by WhatsApp number or create new user"""
        try:
            user = self.get_by_whatsapp(whatsapp_number)
            if user:
                return user
            
            # Create new user with WhatsApp number
            user = User(
                whatsapp_number=whatsapp_number,
                role=role,
                is_verified=True,  # WhatsApp users are automatically verified
                status="Active"
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created new user with WhatsApp number {whatsapp_number}")
            return user
            
        except Exception as e:
            logger.error(f"Error getting or creating user with WhatsApp number {whatsapp_number}: {str(e)}")
            self.db.rollback()
            raise
    
    def save(self, user: User) -> User:
        """Save user to database"""
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error saving user {user.id}: {str(e)}")
            self.db.rollback()
            raise
    
    def update(self, user: User) -> User:
        """Update user in database"""
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error updating user {user.id}: {str(e)}")
            self.db.rollback()
            raise
    
    def set_verified(self, user: User) -> User:
        """Mark user as verified"""
        try:
            user.is_verified = True
            user.mark_verified()
            return self.update(user)
        except Exception as e:
            logger.error(f"Error setting user {user.id} as verified: {str(e)}")
            raise
    
    def update_last_login(self, user: User) -> User:
        """Update user's last login timestamp"""
        try:
            user.update_last_login()
            return self.update(user)
        except Exception as e:
            logger.error(f"Error updating last login for user {user.id}: {str(e)}")
            raise
    
    def update_last_active(self, user: User) -> User:
        """Update user's last active timestamp"""
        try:
            user.update_last_active()
            return self.update(user)
        except Exception as e:
            logger.error(f"Error updating last active for user {user.id}: {str(e)}")
            raise
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        try:
            return self.db.query(User).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
    
    def get_active_users(self) -> List[User]:
        """Get all active users"""
        try:
            return self.db.query(User).filter(User.status == "Active").all()
        except Exception as e:
            logger.error(f"Error getting active users: {str(e)}")
            return []
    
    def delete_user(self, user: User) -> bool:
        """Delete user from database"""
        try:
            self.db.delete(user)
            self.db.commit()
            logger.info(f"Deleted user {user.id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user {user.id}: {str(e)}")
            self.db.rollback()
            return False