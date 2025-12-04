import pyotp
import qrcode
import io
import base64
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TOTPService:
    def __init__(self):
        self.totp = pyotp.TOTP(pyotp.random_base32())
        self.backup_code_length = 8
        self.backup_code_count = 10
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret"""
        try:
            secret = pyotp.random_base32()
            logger.info(f"Generated new TOTP secret: {secret}")
            return secret
        except Exception as e:
            logger.error(f"Failed to generate TOTP secret: {str(e)}")
            raise
    
    def generate_provisioning_uri(self, email: str, secret: str, issuer: str = "RecruitmentApp") -> str:
        """Generate TOTP provisioning URI"""
        try:
            uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=email,
                issuer_name=issuer
            )
            logger.info(f"Generated TOTP provisioning URI for {email}")
            return uri
        except Exception as e:
            logger.error(f"Failed to generate TOTP provisioning URI: {str(e)}")
            raise
    
    def generate_qr_code(self, provisioning_uri: str) -> str:
        """Generate QR code for TOTP setup"""
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            logger.info("Generated TOTP QR code")
            return img_str
        except Exception as e:
            logger.error(f"Failed to generate TOTP QR code: {str(e)}")
            raise
    
    def verify_totp(self, user, totp_code: str) -> bool:
        """Verify TOTP code for user"""
        try:
            if not user.totp_secret:
                logger.warning("User has no TOTP secret")
                return False
            
            # Create TOTP object
            totp = pyotp.TOTP(user.totp_secret)
            
            # Verify code
            is_valid = totp.verify(totp_code, valid_window=1)
            
            if is_valid:
                logger.info(f"Valid TOTP code for user {user.id}")
            else:
                logger.warning(f"Invalid TOTP code for user {user.id}")
            
            return is_valid
        except Exception as e:
            logger.error(f"Failed to verify TOTP code: {str(e)}")
            return False
    
    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes for TOTP"""
        try:
            backup_codes = []
            for _ in range(self.backup_code_count):
                code = ''.join(pyotp.random_base32()[:self.backup_code_length])
                backup_codes.append(code)
            
            logger.info(f"Generated {len(backup_codes)} backup codes")
            return backup_codes
        except Exception as e:
            logger.error(f"Failed to generate backup codes: {str(e)}")
            raise
    
    def verify_backup_code(self, user, backup_code: str) -> bool:
        """Verify backup code for user"""
        try:
            if not user.backup_codes:
                logger.warning("User has no backup codes")
                return False
            
            # Check if backup code is valid
            if user.is_backup_code_valid(backup_code):
                logger.info(f"Valid backup code used for user {user.id}")
                return True
            else:
                logger.warning(f"Invalid backup code for user {user.id}")
                return False
        except Exception as e:
            logger.error(f"Failed to verify backup code: {str(e)}")
            return False
    
    def generate_recovery_codes(self, count: int = 10) -> List[str]:
        """Generate recovery codes (alternative to backup codes)"""
        try:
            recovery_codes = []
            for _ in range(count):
                # Generate more secure recovery codes
                code = ''.join(pyotp.random_base32()[:12])
                recovery_codes.append(code)
            
            logger.info(f"Generated {len(recovery_codes)} recovery codes")
            return recovery_codes
        except Exception as e:
            logger.error(f"Failed to generate recovery codes: {str(e)}")
            raise
    
    def enable_totp(self, user, secret: str) -> bool:
        """Enable TOTP for user"""
        try:
            user.set_totp_secret(secret)
            user.enable_totp()
            logger.info(f"Enabled TOTP for user {user.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to enable TOTP: {str(e)}")
            return False
    
    def disable_totp(self, user) -> bool:
        """Disable TOTP for user"""
        try:
            user.disable_totp()
            logger.info(f"Disabled TOTP for user {user.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to disable TOTP: {str(e)}")
            return False
    
    def get_totp_info(self, user) -> Dict[str, Any]:
        """Get TOTP information for user"""
        try:
            return {
                "enabled": user.totp_enabled,
                "backup_codes_remaining": len(user.backup_codes) if user.backup_codes else 0,
                "has_recovery_codes": hasattr(user, 'recovery_codes') and user.recovery_codes,
                "recovery_codes_remaining": len(user.recovery_codes) if hasattr(user, 'recovery_codes') else 0
            }
        except Exception as e:
            logger.error(f"Failed to get TOTP info: {str(e)}")
            return {}
    
    def rotate_totp_secret(self, user) -> str:
        """Rotate TOTP secret for user"""
        try:
            # Generate new secret
            new_secret = self.generate_secret()
            
            # Disable old TOTP
            self.disable_totp(user)
            
            # Set new secret but don't enable yet
            user.set_totp_secret(new_secret)
            
            logger.info(f"Rotated TOTP secret for user {user.id}")
            return new_secret
        except Exception as e:
            logger.error(f"Failed to rotate TOTP secret: {str(e)}")
            raise
    
    def validate_totp_setup(self, user, totp_code: str) -> bool:
        """Validate TOTP setup by verifying a code"""
        try:
            if not user.totp_secret:
                logger.warning("User has no TOTP secret to validate")
                return False
            
            return self.verify_totp(user, totp_code)
        except Exception as e:
            logger.error(f"Failed to validate TOTP setup: {str(e)}")
            return False
    
    def get_totp_remaining_time(self, user) -> Optional[int]:
        """Get remaining time for current TOTP code"""
        try:
            if not user.totp_secret:
                return None
            
            totp = pyotp.TOTP(user.totp_secret)
            remaining_time = totp.interval - (datetime.utcnow().timestamp() % totp.interval)
            
            return int(remaining_time)
        except Exception as e:
            logger.error(f"Failed to get TOTP remaining time: {str(e)}")
            return None
    
    def test_totp_code(self, secret: str, totp_code: str) -> bool:
        """Test TOTP code with given secret"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(totp_code, valid_window=1)
        except Exception as e:
            logger.error(f"Failed to test TOTP code: {str(e)}")
            return False
    
    def generate_totp_codes(self, secret: str, count: int = 5) -> List[str]:
        """Generate upcoming TOTP codes for testing"""
        try:
            totp = pyotp.TOTP(secret)
            codes = []
            
            for i in range(count):
                # Generate code for future time windows
                future_time = datetime.utcnow() + timedelta(seconds=i * totp.interval)
                codes.append(totp.at(future_time))
            
            return codes
        except Exception as e:
            logger.error(f"Failed to generate TOTP codes: {str(e)}")
            return []
    
    def backup_codes_to_json(self, backup_codes: List[str]) -> str:
        """Convert backup codes to JSON string"""
        try:
            import json
            return json.dumps(backup_codes, indent=2)
        except Exception as e:
            logger.error(f"Failed to convert backup codes to JSON: {str(e)}")
            raise
    
    def backup_codes_from_json(self, json_str: str) -> List[str]:
        """Convert JSON string to backup codes"""
        try:
            import json
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to convert JSON to backup codes: {str(e)}")
            raise
    
    def is_backup_code_valid_format(self, code: str) -> bool:
        """Check if backup code is in valid format"""
        try:
            # Basic validation - adjust according to your requirements
            return len(code) >= 6 and len(code) <= 12 and code.isalnum()
        except Exception as e:
            logger.error(f"Failed to validate backup code format: {str(e)}")
            return False
    
    def cleanup_expired_backup_codes(self, user) -> int:
        """Clean up expired backup codes"""
        try:
            if not user.backup_codes:
                return 0
            
            # In a real implementation, you might have expiration logic
            # For now, we'll just return the count
            initial_count = len(user.backup_codes)
            
            # This is a placeholder - implement your expiration logic here
            # For example, you might want to remove codes that are older than X days
            
            logger.info(f"Cleaned up expired backup codes for user {user.id}")
            return initial_count - len(user.backup_codes)
        except Exception as e:
            logger.error(f"Failed to cleanup expired backup codes: {str(e)}")
            return 0
    
    def get_totp_statistics(self) -> Dict[str, Any]:
        """Get TOTP service statistics"""
        try:
            return {
                "service_name": "TOTP Service",
                "version": "1.0.0",
                "supported_algorithms": ["SHA1", "SHA256", "SHA512"],
                "default_interval": 30,
                "default_digits": 6,
                "backup_code_length": self.backup_code_length,
                "backup_code_count": self.backup_code_count
            }
        except Exception as e:
            logger.error(f"Failed to get TOTP statistics: {str(e)}")
            return {}