#!/usr/bin/env python3
"""
Simplified test for the authentication system
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_otp_service():
    """Test OTP service functionality"""
    logger.info("Testing OTP Service...")
    
    try:
        from backend_app.security.otp_service import OTPService
        
        # Mock user repository
        mock_user_repo = Mock()
        mock_user = Mock()
        mock_user.phone = "+1234567890"
        mock_user.update_otp = Mock()
        mock_user.clear_otp = Mock()
        mock_user.is_otp_valid = Mock(return_value=True)
        
        otp_service = OTPService(mock_user_repo)
        
        # Test OTP generation
        otp = otp_service.generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()
        logger.info(f"✓ OTP generated: {otp}")
        
        # Test OTP verification
        result = otp_service.verify_otp(mock_user, otp)
        assert result is True
        logger.info("✓ OTP verification works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ OTP Service test failed: {str(e)}")
        return False

def test_token_manager():
    """Test token manager functionality"""
    logger.info("Testing Token Manager...")
    
    try:
        from backend_app.security.token_manager import TokenManager
        
        token_manager = TokenManager()
        
        # Test token creation
        data = {"sub": "user123", "role": "candidate"}
        access_token = token_manager.create_access_token(data)
        refresh_token = token_manager.create_refresh_token(data)
        
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert len(access_token) > 0
        assert len(refresh_token) > 0
        logger.info("✓ Tokens created successfully")
        
        # Test token verification
        payload = token_manager.verify_token(access_token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["role"] == "candidate"
        logger.info("✓ Token verification works")
        
        # Test user ID extraction
        user_id = token_manager.get_user_id_from_token(access_token)
        assert user_id == "user123"
        logger.info("✓ User ID extraction works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Token Manager test failed: {str(e)}")
        return False

def test_user_model():
    """Test User model functionality"""
    logger.info("Testing User Model...")
    
    try:
        from backend_app.models.users import User
        from datetime import datetime
        
        # Create user instance
        user = User(
            phone="+1234567890",
            role="candidate",
            is_verified=False
        )
        
        # Test OTP validation
        user.update_otp("123456", datetime.utcnow() + timedelta(minutes=5))
        assert user.is_otp_valid("123456") is True
        assert user.is_otp_valid("000000") is False
        logger.info("✓ OTP validation works")
        
        # Test OTP clearing
        user.clear_otp()
        assert user.otp_code is None
        assert user.otp_expires_at is None
        logger.info("✓ OTP clearing works")
        
        # Test user verification
        user.mark_verified()
        assert user.is_verified is True
        logger.info("✓ User verification works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ User Model test failed: {str(e)}")
        return False

def test_user_repository():
    """Test User Repository functionality"""
    logger.info("Testing User Repository...")
    
    try:
        from backend_app.repositories.user_repo import UserRepository
        
        # Mock database session
        mock_db = Mock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.phone = "+1234567890"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        user_repo = UserRepository(mock_db)
        
        # Test user retrieval
        user = user_repo.get_by_phone("+1234567890")
        assert user is not None
        assert user.phone == "+1234567890"
        logger.info("✓ User retrieval works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ User Repository test failed: {str(e)}")
        return False

def test_schemas():
    """Test data schemas"""
    logger.info("Testing Data Schemas...")
    
    try:
        from backend_app.shared.schemas import LoginRequest, VerifyOTPRequest
        
        # Test login request validation
        login_data = {"phone": "+1234567890"}
        login_request = LoginRequest(**login_data)
        assert login_request.phone == "1234567890"
        logger.info("✓ Login schema validation works")
        
        # Test OTP verification request validation
        otp_data = {"phone": "+1234567890", "otp_code": "123456"}
        otp_request = VerifyOTPRequest(**otp_data)
        assert otp_request.phone == "1234567890"
        assert otp_request.otp_code == "123456"
        logger.info("✓ OTP verification schema validation works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Schema validation test failed: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    logger.info("Testing API Endpoints...")
    
    try:
        from fastapi.testclient import TestClient
        from backend_app.main import app
        
        client = TestClient(app)
        
        # Test login endpoint
        response = client.post("/auth/login", json={"phone": "+1234567890"})
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "phone" in data
        assert "otp_code" in data
        logger.info("✓ Login endpoint works")
        
        # Test OTP verification endpoint
        otp_code = data["otp_code"]
        response = client.post("/auth/verify-otp", json={
            "phone": "+1234567890",
            "otp_code": otp_code
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        logger.info("✓ OTP verification endpoint works")
        
        # Test current user endpoint
        access_token = data["access_token"]
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "phone" in data
        logger.info("✓ Current user endpoint works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ API endpoint test failed: {str(e)}")
        return False

def test_authentication_flow():
    """Test complete authentication flow"""
    logger.info("Testing Complete Authentication Flow...")
    
    try:
        from fastapi.testclient import TestClient
        from backend_app.main import app
        
        client = TestClient(app)
        
        # Step 1: Login
        response = client.post("/auth/login", json={"phone": "+1234567890"})
        assert response.status_code == 200
        login_data = response.json()
        otp_code = login_data["otp_code"]
        logger.info("✓ Step 1: Login successful")
        
        # Step 2: Verify OTP
        response = client.post("/auth/verify-otp", json={
            "phone": "+1234567890",
            "otp_code": otp_code
        })
        assert response.status_code == 200
        auth_data = response.json()
        access_token = auth_data["access_token"]
        refresh_token = auth_data["refresh_token"]
        logger.info("✓ Step 2: OTP verification successful")
        
        # Step 3: Get current user
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["phone"] == "+1234567890"
        logger.info("✓ Step 3: User retrieval successful")
        
        # Step 4: Refresh token
        response = client.post("/auth/refresh-token", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        refresh_data = response.json()
        assert "access_token" in refresh_data
        assert "refresh_token" in refresh_data
        logger.info("✓ Step 4: Token refresh successful")
        
        # Step 5: Logout
        response = client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        logout_data = response.json()
        assert logout_data["status"] == "logged_out"
        logger.info("✓ Step 5: Logout successful")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Authentication flow test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and generate report"""
    logger.info("Starting Authentication System Tests...")
    
    tests = [
        ("User Model", test_user_model),
        ("User Repository", test_user_repository),
        ("Data Schemas", test_schemas),
        ("OTP Service", test_otp_service),
        ("Token Manager", test_token_manager),
        ("API Endpoints", test_api_endpoints),
        ("Authentication Flow", test_authentication_flow)
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                failed += 1
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_name} FAILED with exception: {str(e)}")
            results.append((test_name, False))
    
    # Generate test report
    report = {
        "test_summary": {
            "date": datetime.now().isoformat(),
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(tests)) * 100 if tests else 0
        },
        "test_results": results,
        "recommendations": []
    }
    
    # Add recommendations
    if failed > 0:
        report["recommendations"].append(f"{failed} tests failed. Please review the output above.")
    else:
        report["recommendations"].append("All tests passed successfully!")
    
    # Save report
    report_file = "test_results.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("AUTHENTICATION SYSTEM TEST SUMMARY")
    print("="*60)
    print(f"Date: {report['test_summary']['date']}")
    print(f"Total Tests: {report['test_summary']['total_tests']}")
    print(f"Passed: {report['test_summary']['passed']}")
    print(f"Failed: {report['test_summary']['failed']}")
    print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
    print("="*60)
    
    if report["recommendations"]:
        print("\nRECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"• {rec}")
    
    print(f"\nDetailed report saved to: {report_file}")
    
    return report['test_summary']['success_rate'] >= 90

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)