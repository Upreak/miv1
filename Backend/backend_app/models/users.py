from sqlalchemy import Column, String, DateTime, Boolean, func, JSON, Integer
import uuid
from datetime import datetime, timedelta
from ..db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Primary identifier - phone number
    phone = Column(String, unique=True, nullable=False, index=True)
    
    # Email for social login and fallback
    email = Column(String, unique=True, nullable=True, index=True)
    
    # Social login identifiers
    whatsapp_number = Column(String, unique=True, nullable=True)
    telegram_id = Column(String, unique=True, nullable=True)
    
    # OTP fields
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    otp_attempts = Column(Integer, default=0)
    otp_locked_until = Column(DateTime, nullable=True)
    
    # Multi-factor authentication
    totp_secret = Column(String, nullable=True)
    totp_enabled = Column(Boolean, default=False)
    backup_codes = Column(JSON, nullable=True)  # Store as JSON array
    
    # Video OTP fields
    video_otp_session_id = Column(String, nullable=True)
    video_otp_expires_at = Column(DateTime, nullable=True)
    video_otp_data = Column(JSON, nullable=True)  # Store video OTP data
    
    # Social login fields
    google_id = Column(String, unique=True, nullable=True)
    facebook_id = Column(String, unique=True, nullable=True)
    linkedin_id = Column(String, unique=True, nullable=True)
    
    # Password fields (for social login fallback)
    password_hash = Column(String, nullable=True)
    
    # User details
    role = Column(String, default="CANDIDATE")  # ADMIN, RECRUITER, CANDIDATE
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Verification status
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    status = Column(String, default="Active")
    
    # Session management
    current_refresh_token = Column(String, nullable=True)
    refresh_token_version = Column(Integer, default=0)
    session_timeout = Column(Integer, default=1800)  # 30 minutes in seconds
    last_activity = Column(DateTime(timezone=True))
    
    # Security settings
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    require_mfa = Column(Boolean, default=False)
    preferred_auth_method = Column(String, default="phone")  # phone, email, social
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    last_active = Column(DateTime(timezone=True))
    password_changed_at = Column(DateTime(timezone=True))
    
    # Preferences
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    notifications_enabled = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone}, email={self.email}, role={self.role})>"
    
    def is_otp_valid(self, otp_code: str) -> bool:
        """Check if OTP is valid and not expired"""
        if not self.otp_code or not self.otp_expires_at:
            return False
        
        if self.otp_code != otp_code:
            return False
            
        if datetime.utcnow() > self.otp_expires_at:
            return False
            
        return True
    
    def update_otp(self, otp_code: str, expires_at: datetime):
        """Update OTP code and expiration"""
        self.otp_code = otp_code
        self.otp_expires_at = expires_at
        self.otp_attempts = 0
    
    def clear_otp(self):
        """Clear OTP fields after successful verification"""
        self.otp_code = None
        self.otp_expires_at = None
        self.otp_attempts = 0
        self.otp_locked_until = None
    
    def increment_otp_attempts(self):
        """Increment OTP attempt count and handle lockout"""
        self.otp_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.otp_attempts >= 5:
            self.otp_locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        return self.otp_attempts
    
    def reset_otp_attempts(self):
        """Reset OTP attempt count"""
        self.otp_attempts = 0
        self.otp_locked_until = None
    
    def is_otp_locked(self) -> bool:
        """Check if user is locked out due to too many OTP attempts"""
        if not self.otp_locked_until:
            return False
        
        return datetime.utcnow() < self.otp_locked_until
    
    def mark_verified(self):
        """Mark user as verified"""
        self.is_verified = True
        self.phone_verified = True
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.last_active = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def is_session_expired(self) -> bool:
        """Check if user session has expired"""
        if not self.last_activity:
            return True
        
        timeout_seconds = self.session_timeout or 1800
        return datetime.utcnow() > self.last_activity + timedelta(seconds=timeout_seconds)
    
    def update_session_activity(self):
        """Update session activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def increment_login_attempts(self):
        """Increment login attempt count"""
        self.login_attempts += 1
        
        # Lock account after 5 failed login attempts
        if self.login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        return self.login_attempts
    
    def reset_login_attempts(self):
        """Reset login attempt count"""
        self.login_attempts = 0
        self.locked_until = None
    
    def is_account_locked(self) -> bool:
        """Check if user account is locked"""
        if not self.locked_until:
            return False
        
        return datetime.utcnow() < self.locked_until
    
    def rotate_refresh_token(self):
        """Rotate refresh token version"""
        self.refresh_token_version += 1
    
    def set_totp_secret(self, secret: str):
        """Set TOTP secret"""
        self.totp_secret = secret
    
    def enable_totp(self):
        """Enable TOTP"""
        self.totp_enabled = True
    
    def disable_totp(self):
        """Disable TOTP"""
        self.totp_enabled = False
        self.totp_secret = None
    
    def add_backup_code(self, code: str):
        """Add backup code"""
        if not self.backup_codes:
            self.backup_codes = []
        
        self.backup_codes.append(code)
    
    def remove_backup_code(self, code: str):
        """Remove backup code"""
        if self.backup_codes and code in self.backup_codes:
            self.backup_codes.remove(code)
    
    def is_backup_code_valid(self, code: str) -> bool:
        """Check if backup code is valid"""
        if not self.backup_codes:
            return False
        
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            return True
        
        return False
    
    def set_video_otp(self, session_id: str, expires_at: datetime, otp_data: dict):
        """Set video OTP data"""
        self.video_otp_session_id = session_id
        self.video_otp_expires_at = expires_at
        self.video_otp_data = otp_data
    
    def clear_video_otp(self):
        """Clear video OTP data"""
        self.video_otp_session_id = None
        self.video_otp_expires_at = None
        self.video_otp_data = None
    
    def is_video_otp_valid(self) -> bool:
        """Check if video OTP is valid"""
        if not self.video_otp_session_id or not self.video_otp_expires_at:
            return False
        
        return datetime.utcnow() < self.video_otp_expires_at
    
    def set_social_login_id(self, provider: str, social_id: str):
        """Set social login ID"""
        if provider == "google":
            self.google_id = social_id
        elif provider == "facebook":
            self.facebook_id = social_id
        elif provider == "linkedin":
            self.linkedin_id = social_id
    
    def get_social_login_id(self, provider: str) -> str:
        """Get social login ID"""
        if provider == "google":
            return self.google_id
        elif provider == "facebook":
            return self.facebook_id
        elif provider == "linkedin":
            return self.linkedin_id
        return None
    
    def has_social_login(self, provider: str) -> bool:
        """Check if user has social login for provider"""
        return self.get_social_login_id(provider) is not None
    
    def set_password_hash(self, password_hash: str):
        """Set password hash"""
        self.password_hash = password_hash
        self.password_changed_at = datetime.utcnow()
    
    def verify_password(self, password_hash: str) -> bool:
        """Verify password hash"""
        return self.password_hash == password_hash
    
    def update_preferences(self, **kwargs):
        """Update user preferences"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "phone": self.phone,
            "email": self.email,
            "whatsapp_number": self.whatsapp_number,
            "telegram_id": self.telegram_id,
            "role": self.role,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "is_verified": self.is_verified,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "totp_enabled": self.totp_enabled,
            "require_mfa": self.require_mfa,
            "preferred_auth_method": self.preferred_auth_method,
            "language": self.language,
            "timezone": self.timezone,
            "notifications_enabled": self.notifications_enabled
        }