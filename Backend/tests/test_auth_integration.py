import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend_app.db.base import Base, get_db
from backend_app.models.users import User
from backend_app.security.otp_service import OTPService
from backend_app.security.token_manager import TokenManager
from backend_app.security.enhanced_auth_service import EnhancedAuthService
from backend_app.security.rate_limiter import RateLimiter
from backend_app.security.social_auth import SocialAuthService
from backend_app.security.totp_service import TOTPService
from backend_app.security.email_service import EmailService
from backend_app.repositories.user_repo import UserRepository
from backend_app.api.auth import router as auth_router
from backend_app.main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestOTPService:
    @pytest.fixture
    def otp_service(self):
        user_repo = Mock(spec=UserRepository)
        return OTPService(user_repo)
    
    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=User)
        user.phone = "+1234567890"
        user.update_otp = Mock()
        user.clear_otp = Mock()
        user.is_otp_valid = Mock(return_value=True)
        return user
    
    def test_generate_otp(self, otp_service):
        otp = otp_service.generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()
    
    def test_send_otp(self, otp_service, mock_user):
        with patch.object(otp_service, '_send_sms') as mock_send_sms:
            otp = otp_service.send_otp(mock_user, send_via_sms=False)
            assert len(otp) == 6
            assert otp.isdigit()
            mock_send_sms.assert_called_once()
    
    def test_verify_otp_valid(self, otp_service, mock_user):
        mock_user.is_otp_valid.return_value = True
        result = otp_service.verify_otp(mock_user, "123456")
        assert result is True
        mock_user.clear_otp.assert_called_once()
    
    def test_verify_otp_invalid(self, otp_service, mock_user):
        mock_user.is_otp_valid.return_value = False
        result = otp_service.verify_otp(mock_user, "123456")
        assert result is False
        mock_user.clear_otp.assert_not_called()

class TestTokenManager:
    @pytest.fixture
    def token_manager(self):
        return TokenManager()
    
    def test_create_access_token(self, token_manager):
        data = {"sub": "user123", "role": "candidate"}
        token = token_manager.create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self, token_manager):
        data = {"sub": "user123", "role": "candidate"}
        token = token_manager.create_refresh_token(data)
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_tokens_for_user(self, token_manager):
        tokens = token_manager.create_tokens_for_user("user123", "candidate")
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"
    
    def test_verify_token_valid(self, token_manager):
        data = {"sub": "user123", "role": "candidate"}
        token = token_manager.create_access_token(data)
        payload = token_manager.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["role"] == "candidate"
    
    def test_verify_token_invalid(self, token_manager):
        payload = token_manager.verify_token("invalid_token")
        assert payload is None
    
    def test_get_user_id_from_token(self, token_manager):
        data = {"sub": "user123", "role": "candidate"}
        token = token_manager.create_access_token(data)
        user_id = token_manager.get_user_id_from_token(token)
        assert user_id == "user123"
    
    def test_get_role_from_token(self, token_manager):
        data = {"sub": "user123", "role": "candidate"}
        token = token_manager.create_access_token(data)
        role = token_manager.get_role_from_token(token)
        assert role == "candidate"

class TestRateLimiter:
    @pytest.fixture
    def rate_limiter(self):
        return RateLimiter()
    
    @pytest.mark.asyncio
    async def test_is_rate_limited(self, rate_limiter):
        # Test first few requests
        for i in range(5):
            result = await rate_limiter.is_rate_limited(f"user_{i}", "auth")
            assert result is False
        
        # Test rate limiting
        result = await rate_limiter.is_rate_limited("user_0", "auth")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_record_attempt(self, rate_limiter):
        await rate_limiter.record_attempt("user_1", "auth")
        # Should not raise any exceptions
        assert True
    
    @pytest.mark.asyncio
    async def test_get_rate_limit_info(self, rate_limiter):
        info = await rate_limiter.get_rate_limit_info("user_2", "auth")
        assert "identifier" in info
        assert "action" in info
        assert "current_count" in info
        assert "max_requests" in info
        assert "remaining_requests" in info

class TestTOTPService:
    @pytest.fixture
    def totp_service(self):
        return TOTPService()
    
    def test_generate_secret(self, totp_service):
        secret = totp_service.generate_secret()
        assert isinstance(secret, str)
        assert len(secret) > 0
    
    def test_generate_provisioning_uri(self, totp_service):
        secret = totp_service.generate_secret()
        uri = totp_service.generate_provisioning_uri("test@example.com", secret)
        assert isinstance(uri, str)
        assert "otpauth" in uri
    
    def test_generate_qr_code(self, totp_service):
        secret = totp_service.generate_secret()
        uri = totp_service.generate_provisioning_uri("test@example.com", secret)
        qr_code = totp_service.generate_qr_code(uri)
        assert isinstance(qr_code, str)
        assert len(qr_code) > 0
    
    def test_generate_backup_codes(self, totp_service):
        codes = totp_service.generate_backup_codes()
        assert len(codes) == 10
        for code in codes:
            assert len(code) >= 6
    
    def test_verify_totp(self, totp_service):
        secret = totp_service.generate_secret()
        totp = totp_service.totp
        valid_code = totp.now()
        
        # Mock user with TOTP secret
        mock_user = Mock()
        mock_user.totp_secret = secret
        
        result = totp_service.verify_totp(mock_user, valid_code)
        assert result is True
    
    def test_verify_totp_invalid(self, totp_service):
        mock_user = Mock()
        mock_user.totp_secret = "invalid_secret"
        
        result = totp_service.verify_totp(mock_user, "123456")
        assert result is False

class TestEmailService:
    @pytest.fixture
    def email_service(self):
        return EmailService()
    
    @pytest.fixture
    def mock_smtp(self):
        with patch('smtplib.SMTP') as mock_smtp_class:
            mock_smtp_instance = mock_smtp_class.return_value.__enter__.return_value
            mock_smtp_instance.send_message = Mock()
            yield mock_smtp_instance
    
    def test_send_otp(self, email_service, mock_smtp):
        result = email_service.send_otp("test@example.com", "123456")
        assert result is True
        mock_smtp.send_message.assert_called_once()
    
    def test_send_welcome_email(self, email_service, mock_smtp):
        result = email_service.send_welcome_email("test@example.com", "John Doe")
        assert result is True
        mock_smtp.send_message.assert_called_once()
    
    def test_send_password_reset(self, email_service, mock_smtp):
        result = email_service.send_password_reset("test@example.com", "reset_token_123")
        assert result is True
        mock_smtp.send_message.assert_called_once()
    
    def test_generate_verification_token(self, email_service):
        token = email_service.generate_verification_token()
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generate_password_reset_token(self, email_service):
        token = email_service.generate_password_reset_token()
        assert isinstance(token, str)
        assert len(token) > 0

class TestSocialAuthService:
    @pytest.fixture
    def social_auth(self):
        return SocialAuthService()
    
    @pytest.mark.asyncio
    async def test_get_google_auth_url(self, social_auth):
        with patch('secrets.token_urlsafe', return_value='test_state'):
            url, state = social_auth.get_google_auth_url()
            assert isinstance(url, str)
            assert "accounts.google.com" in url
            assert state == "test_state"
    
    @pytest.mark.asyncio
    async def test_get_facebook_auth_url(self, social_auth):
        with patch('secrets.token_urlsafe', return_value='test_state'):
            url, state = social_auth.get_facebook_auth_url()
            assert isinstance(url, str)
            assert "facebook.com" in url
            assert state == "test_state"
    
    @pytest.mark.asyncio
    async def test_get_linkedin_auth_url(self, social_auth):
        with patch('secrets.token_urlsafe', return_value='test_state'):
            url, state = social_auth.get_linkedin_auth_url()
            assert isinstance(url, str)
            assert "linkedin.com" in url
            assert state == "test_state"
    
    def test_is_provider_configured(self, social_auth):
        # Test with mock environment variables
        with patch.dict('os.environ', {
            'GOOGLE_CLIENT_ID': 'test_client_id',
            'GOOGLE_CLIENT_SECRET': 'test_client_secret'
        }):
            assert social_auth.is_provider_configured('google') is True
            assert social_auth.is_provider_configured('facebook') is False
    
    def test_get_configured_providers(self, social_auth):
        with patch.dict('os.environ', {
            'GOOGLE_CLIENT_ID': 'test_client_id',
            'GOOGLE_CLIENT_SECRET': 'test_client_secret',
            'FACEBOOK_APP_ID': 'test_app_id',
            'FACEBOOK_APP_SECRET': 'test_app_secret'
        }):
            providers = social_auth.get_configured_providers()
            assert 'google' in providers
            assert 'facebook' in providers

class TestEnhancedAuthService:
    @pytest.fixture
    def auth_service(self):
        db = TestingSessionLocal()
        user_repo = UserRepository(db)
        return EnhancedAuthService(db)
    
    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=User)
        user.id = "user123"
        user.phone = "+1234567890"
        user.email = "test@example.com"
        user.role = "candidate"
        user.is_verified = False
        user.totp_enabled = False
        user.login_attempts = 0
        user.locked_until = None
        user.increment_login_attempts = Mock()
        user.reset_login_attempts = Mock()
        user.mark_verified = Mock()
        user.update_last_login = Mock()
        user.clear_otp = Mock()
        user.to_dict = Mock(return_value={"id": "user123", "role": "candidate"})
        return user
    
    @pytest.mark.asyncio
    async def test_authenticate_by_phone(self, auth_service, mock_user):
        with patch.object(auth_service.user_repo, 'get_by_phone_or_create', return_value=mock_user):
            with patch.object(auth_service.otp_service, 'send_otp', return_value="123456"):
                result = await auth_service.authenticate_user("+1234567890", "phone")
                assert result["status"] == "otp_sent"
                assert result["otp_code"] == "123456"
    
    @pytest.mark.asyncio
    async def test_authenticate_by_phone_with_otp(self, auth_service, mock_user):
        with patch.object(auth_service.user_repo, 'get_by_phone', return_value=mock_user):
            with patch.object(auth_service.otp_service, 'verify_otp', return_value=True):
                mock_user.is_verified = True
                result = await auth_service.authenticate_user("+1234567890", "phone", otp_code="123456")
                assert result["status"] == "authenticated"
                assert "tokens" in result
    
    @pytest.mark.asyncio
    async def test_authenticate_by_email(self, auth_service, mock_user):
        with patch.object(auth_service.user_repo, 'get_by_email_or_create', return_value=mock_user):
            with patch.object(auth_service.email_service, 'send_otp', return_value="123456"):
                result = await auth_service.authenticate_user("test@example.com", "email")
                assert result["status"] == "otp_sent"
    
    @pytest.mark.asyncio
    async def test_authenticate_by_email_with_otp(self, auth_service, mock_user):
        with patch.object(auth_service.user_repo, 'get_by_email', return_value=mock_user):
            with patch.object(auth_service.email_service, 'verify_otp', return_value=True):
                mock_user.is_verified = True
                result = await auth_service.authenticate_user("test@example.com", "email", otp_code="123456")
                assert result["status"] == "authenticated"
                assert "tokens" in result
    
    @pytest.mark.asyncio
    async def test_authenticate_by_totp(self, auth_service, mock_user):
        mock_user.totp_enabled = True
        with patch.object(auth_service.user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(auth_service.totp_service, 'verify_totp', return_value=True):
                result = await auth_service.authenticate_user("user123", "totp", totp_code="123456")
                assert result["status"] == "authenticated"
                assert "tokens" in result
    
    @pytest.mark.asyncio
    async def test_verify_mfa(self, auth_service, mock_user):
        with patch.object(auth_service.totp_service, 'verify_totp', return_value=True):
            result = await auth_service.verify_mfa(mock_user, "123456", "totp")
            assert result["status"] == "authenticated"
            assert "tokens" in result
    
    @pytest.mark.asyncio
    async def test_refresh_tokens(self, auth_service, mock_user):
        with patch.object(auth_service.token_manager, 'is_refresh_token', return_value=True):
            with patch.object(auth_service.token_manager, 'verify_token', return_value={"sub": "user123"}):
                with patch.object(auth_service.user_repo, 'get_by_id', return_value=mock_user):
                    result = await auth_service.refresh_tokens("refresh_token_123")
                    assert result["status"] == "tokens_refreshed"
                    assert "tokens" in result
    
    @pytest.mark.asyncio
    async def test_logout(self, auth_service, mock_user):
        result = await auth_service.logout(mock_user)
        assert result["status"] == "logged_out"
        assert result["message"] == "Successfully logged out"

class TestAPIEndpoints:
    def test_login_endpoint(self):
        response = client.post("/auth/login", json={"phone": "+1234567890"})
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "phone" in data
        assert "otp_code" in data
    
    def test_verify_otp_endpoint(self):
        # First send OTP
        login_response = client.post("/auth/login", json={"phone": "+1234567890"})
        otp_code = login_response.json()["otp_code"]
        
        # Then verify OTP
        response = client.post("/auth/verify-otp", json={
            "phone": "+1234567890",
            "otp_code": otp_code
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
    
    def test_get_current_user_endpoint(self):
        # First login
        login_response = client.post("/auth/login", json={"phone": "+1234567890"})
        otp_code = login_response.json()["otp_code"]
        
        # Verify OTP
        verify_response = client.post("/auth/verify-otp", json={
            "phone": "+1234567890",
            "otp_code": otp_code
        })
        access_token = verify_response.json()["access_token"]
        
        # Get current user
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "phone" in data
    
    def test_refresh_token_endpoint(self):
        # First login
        login_response = client.post("/auth/login", json={"phone": "+1234567890"})
        otp_code = login_response.json()["otp_code"]
        
        # Verify OTP
        verify_response = client.post("/auth/verify-otp", json={
            "phone": "+1234567890",
            "otp_code": otp_code
        })
        refresh_token = verify_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post("/auth/refresh-token", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_logout_endpoint(self):
        # First login
        login_response = client.post("/auth/login", json={"phone": "+1234567890"})
        otp_code = login_response.json()["otp_code"]
        
        # Verify OTP
        verify_response = client.post("/auth/verify-otp", json={
            "phone": "+1234567890",
            "otp_code": otp_code
        })
        access_token = verify_response.json()["access_token"]
        
        # Logout
        response = client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "logged_out"

class TestIntegrationScenarios:
    @pytest.mark.asyncio
    async def test_complete_authentication_flow(self, auth_service):
        """Test complete authentication flow from phone login to token refresh"""
        # Step 1: Phone login
        result1 = await auth_service.authenticate_user("+1234567890", "phone")
        assert result1["status"] == "otp_sent"
        otp_code = result1["otp_code"]
        
        # Step 2: Verify OTP
        result2 = await auth_service.authenticate_user("+1234567890", "phone", otp_code=otp_code)
        assert result2["status"] == "authenticated"
        access_token = result2["tokens"]["access_token"]
        refresh_token = result2["tokens"]["refresh_token"]
        
        # Step 3: Refresh token
        result3 = await auth_service.refresh_tokens(refresh_token)
        assert result3["status"] == "tokens_refreshed"
        new_access_token = result3["tokens"]["access_token"]
        
        # Step 4: Logout
        result4 = await auth_service.logout(result2["user"], refresh_token)
        assert result4["status"] == "logged_out"
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "new_access_token": new_access_token
        }
    
    @pytest.mark.asyncio
    async def test_multi_factor_authentication_flow(self, auth_service):
        """Test MFA flow with TOTP"""
        # Step 1: Setup TOTP
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.totp_secret = None
        mock_user.totp_enabled = False
        
        with patch.object(auth_service.user_repo, 'get_by_id', return_value=mock_user):
            result1 = await auth_service.setup_totp(mock_user)
            assert result1["status"] == "totp_setup"
            assert "provisioning_uri" in result1
            assert "backup_codes" in result1
        
        # Step 2: Enable TOTP
        mock_user.totp_secret = result1["secret"]
        mock_user.totp_enabled = False
        
        with patch.object(auth_service.user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(auth_service.totp_service, 'verify_totp', return_value=True):
                result2 = await auth_service.enable_totp(mock_user, "123456")
                assert result2["status"] == "totp_enabled"
        
        # Step 3: Authenticate with TOTP
        mock_user.totp_enabled = True
        
        with patch.object(auth_service.user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(auth_service.totp_service, 'verify_totp', return_value=True):
                result3 = await auth_service.authenticate_user("user123", "totp", totp_code="123456")
                assert result3["status"] == "authenticated"
                assert "tokens" in result3
        
        return {
            "totp_setup": result1,
            "totp_enabled": result2,
            "authenticated": result3
        }
    
    @pytest.mark.asyncio
    async def test_social_authentication_flow(self, auth_service):
        """Test social authentication flow"""
        # Step 1: Get Google auth URL
        social_auth = SocialAuthService()
        auth_url, state = social_auth.get_google_auth_url()
        assert "accounts.google.com" in auth_url
        
        # Step 2: Mock token exchange
        mock_token_data = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600,
            "token_type": "bearer",
            "provider": "google",
            "user": {
                "id": "google_123",
                "email": "test@gmail.com",
                "name": "Test User"
            }
        }
        
        with patch.object(social_auth, 'exchange_code_for_token', return_value=mock_token_data):
            # Step 3: Authenticate with social token
            result = await auth_service.authenticate_user("google_123", "social", 
                                                         provider="google", 
                                                         access_token="mock_access_token")
            assert result["status"] == "authenticated"
            assert "tokens" in result
        
        return {
            "auth_url": auth_url,
            "state": state,
            "result": result
        }

class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_invalid_otp(self, auth_service):
        """Test handling of invalid OTP"""
        mock_user = Mock()
        mock_user.phone = "+1234567890"
        
        with patch.object(auth_service.user_repo, 'get_by_phone', return_value=mock_user):
            with patch.object(auth_service.otp_service, 'verify_otp', return_value=False):
                with pytest.raises(Exception):
                    await auth_service.authenticate_user("+1234567890", "phone", otp_code="invalid")
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, rate_limiter):
        """Test rate limiting functionality"""
        # Test rate limiting
        for i in range(6):  # Exceed limit
            result = await rate_limiter.is_rate_limited("test_user", "auth")
        
        # Should be rate limited now
        assert result is True
    
    @pytest.mark.asyncio
    async def test_expired_token(self, token_manager):
        """Test handling of expired tokens"""
        # Create token with short expiry
        data = {"sub": "user123", "role": "candidate"}
        token = token_manager.create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        # Try to verify expired token
        payload = token_manager.verify_token(token)
        assert payload is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])