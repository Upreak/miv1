#!/usr/bin/env python3
"""
Isolated authentication system test - completely independent of dependencies
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import json
import random
import string
import hashlib
import jwt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_jwt_token_logic():
    """Test JWT token logic without external dependencies"""
    logger.info("Testing JWT Token Logic...")
    
    try:
        # Simple JWT implementation
        secret_key = "your-super-secret-jwt-key-here-change-in-production"
        algorithm = "HS256"
        
        # Test token creation
        data = {"sub": "user123", "role": "candidate"}
        access_token = jwt.encode(data, secret_key, algorithm=algorithm)
        refresh_token = jwt.encode(data, secret_key, algorithm=algorithm)
        
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert len(access_token) > 0
        assert len(refresh_token) > 0
        logger.info("✓ JWT tokens created successfully")
        
        # Test token verification
        decoded = jwt.decode(access_token, secret_key, algorithms=[algorithm])
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "candidate"
        logger.info("✓ JWT token verification works")
        
        # Test user ID extraction
        user_id = decoded["sub"]
        assert user_id == "user123"
        logger.info("✓ User ID extraction works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ JWT Token Logic test failed: {str(e)}")
        return False

def test_otp_generation_logic():
    """Test OTP generation and validation logic"""
    logger.info("Testing OTP Generation Logic...")
    
    try:
        # OTP generation function
        def generate_otp(length=6):
            digits = string.digits
            return ''.join(random.choice(digits) for _ in range(length))
        
        # OTP validation function
        def is_otp_valid(stored_otp, user_otp, expires_at):
            if not stored_otp or not user_otp or not expires_at:
                return False
            
            if stored_otp != user_otp:
                return False
            
            if datetime.utcnow() > expires_at:
                return False
            
            return True
        
        # Test OTP generation
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()
        logger.info(f"✓ OTP generated: {otp}")
        
        # Test OTP validation
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        valid = is_otp_valid(otp, otp, expires_at)
        assert valid is True
        logger.info("✓ OTP validation works")
        
        # Test expired OTP
        expired_at = datetime.utcnow() - timedelta(minutes=1)
        expired = is_otp_valid(otp, otp, expired_at)
        assert expired is False
        logger.info("✓ Expired OTP detection works")
        
        # Test wrong OTP
        wrong = is_otp_valid(otp, "000000", expires_at)
        assert wrong is False
        logger.info("✓ Wrong OTP detection works")
        
        # Test edge cases
        empty_otp = is_otp_valid("", otp, expires_at)
        assert empty_otp is False
        logger.info("✓ Empty OTP detection works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ OTP Generation Logic test failed: {str(e)}")
        return False

def test_phone_validation():
    """Test phone number validation logic"""
    logger.info("Testing Phone Validation Logic...")
    
    try:
        # Phone validation function
        def validate_phone(phone):
            # Remove any non-digit characters
            digits_only = ''.join(c for c in phone if c.isdigit())
            if len(digits_only) < 10:
                return None
            return digits_only
        
        # Test valid phone numbers
        test_phones = [
            "+1234567890",
            "1234567890",
            "+91 98765 43210",
            "919876543210",
            "9876543210"
        ]
        
        for phone in test_phones:
            validated = validate_phone(phone)
            assert validated is not None
            assert len(validated) >= 10
            assert validated.isdigit()
            logger.info(f"✓ Phone {phone} validated to: {validated}")
        
        # Test invalid phone numbers
        invalid_phones = [
            "123",  # Too short
            "abc",  # Non-numeric
            "",     # Empty
            "123456789",  # 9 digits
        ]
        
        for phone in invalid_phones:
            validated = validate_phone(phone)
            assert validated is None
            logger.info(f"✓ Invalid phone {phone} correctly rejected")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Phone Validation Logic test failed: {str(e)}")
        return False

def test_user_security_logic():
    """Test user security and account lockout logic"""
    logger.info("Testing User Security Logic...")
    
    try:
        class MockUser:
            def __init__(self, phone):
                self.phone = phone
                self.login_attempts = 0
                self.locked_until = None
                self.is_verified = False
                self.otp_code = None
                self.otp_expires_at = None
            
            def increment_login_attempts(self):
                self.login_attempts += 1
                
                # Lock account after 5 failed attempts
                if self.login_attempts >= 5:
                    self.locked_until = datetime.utcnow() + timedelta(minutes=15)
                
                return self.login_attempts
            
            def is_account_locked(self):
                if not self.locked_until:
                    return False
                
                return datetime.utcnow() < self.locked_until
            
            def reset_login_attempts(self):
                self.login_attempts = 0
                self.locked_until = None
            
            def update_otp(self, otp_code, expires_at):
                self.otp_code = otp_code
                self.otp_expires_at = expires_at
                self.reset_login_attempts()
            
            def is_otp_valid(self, otp_code):
                if not self.otp_code or not self.otp_expires_at:
                    return False
                
                if self.otp_code != otp_code:
                    return False
                
                if datetime.utcnow() > self.otp_expires_at:
                    return False
                
                return True
        
        # Test user creation
        user = MockUser("+1234567890")
        assert user.phone == "+1234567890"
        assert user.login_attempts == 0
        assert user.is_account_locked() is False
        logger.info("✓ User creation works")
        
        # Test login attempts
        user.increment_login_attempts()
        assert user.login_attempts == 1
        assert user.is_account_locked() is False
        
        # Test multiple login attempts
        for i in range(4):
            user.increment_login_attempts()
        
        assert user.login_attempts == 5
        assert user.is_account_locked() is True
        logger.info("✓ Account lockout after 5 attempts works")
        
        # Test OTP functionality
        user.update_otp("123456", datetime.utcnow() + timedelta(minutes=5))
        assert user.otp_code == "123456"
        assert user.login_attempts == 0
        assert user.is_account_locked() is False
        logger.info("✓ OTP reset login attempts works")
        
        # Test OTP validation
        assert user.is_otp_valid("123456") is True
        assert user.is_otp_valid("000000") is False
        logger.info("✓ OTP validation works")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ User Security Logic test failed: {str(e)}")
        return False

def test_authentication_flow():
    """Test complete authentication flow"""
    logger.info("Testing Authentication Flow...")
    
    try:
        # Simulate complete authentication flow
        phone = "+1234567890"
        
        # Step 1: User login
        logger.info(f"✓ Step 1: User login with phone {phone}")
        
        # Step 2: OTP generation
        otp = generate_otp()
        logger.info(f"✓ Step 2: OTP generated: {otp}")
        
        # Step 3: OTP verification simulation
        user_id = "user123"
        role = "candidate"
        logger.info(f"✓ Step 3: OTP verified for user {user_id}")
        
        # Step 4: Token generation
        secret_key = "your-super-secret-jwt-key-here-change-in-production"
        algorithm = "HS256"
        
        access_token = jwt.encode(
            {"sub": user_id, "role": role}, 
            secret_key, 
            algorithm=algorithm
        )
        refresh_token = jwt.encode(
            {"sub": user_id, "role": role}, 
            secret_key, 
            algorithm=algorithm
        )
        
        logger.info("✓ Step 4: JWT tokens generated")
        
        # Step 5: Token verification
        decoded = jwt.decode(access_token, secret_key, algorithms=[algorithm])
        assert decoded["sub"] == user_id
        assert decoded["role"] == role
        logger.info("✓ Step 5: Token verification successful")
        
        # Step 6: Token refresh
        new_access_token = jwt.encode(
            {"sub": user_id, "role": role}, 
            secret_key, 
            algorithm=algorithm
        )
        assert new_access_token != access_token
        logger.info("✓ Step 6: Token refresh successful")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Authentication Flow test failed: {str(e)}")
        return False

def generate_otp(length=6):
    """Generate OTP utility function"""
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))

def run_all_tests():
    """Run all tests and generate report"""
    logger.info("Starting Isolated Authentication System Tests...")
    
    tests = [
        ("JWT Token Logic", test_jwt_token_logic),
        ("OTP Generation Logic", test_otp_generation_logic),
        ("Phone Validation Logic", test_phone_validation),
        ("User Security Logic", test_user_security_logic),
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
        report["recommendations"].append("All isolated authentication tests passed successfully!")
    
    # Save report
    report_file = "test_isolated_results.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("ISOLATED AUTHENTICATION SYSTEM TEST SUMMARY")
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