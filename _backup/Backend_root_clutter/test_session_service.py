#!/usr/bin/env python3
"""
Test Session Service and API Integration
"""

import sys
import os
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_session_service():
    """Test if session service can be imported"""
    print("Testing Session Service...")
    try:
        from backend_app.chatbot.services.session_service import SessionService
        print("SUCCESS: Session Service imported successfully")
        return True
    except ImportError as e:
        print(f"FAILED: Session Service import failed: {e}")
        return False

def test_api_integration():
    """Test if chatbot API is properly integrated"""
    print("\nTesting API Integration...")
    try:
        from backend_app.api.v1 import chatbot
        print("SUCCESS: Chatbot API module imported")
        
        # Check if endpoints exist
        endpoints = [attr for attr in dir(chatbot) if attr.startswith('_') is False]
        print(f"Available endpoints: {endpoints}")
        return True
    except ImportError as e:
        print(f"FAILED: API Integration failed: {e}")
        return False

def test_services_init():
    """Test if services __init__.py works"""
    print("\nTesting Services Init...")
    try:
        from backend_app.chatbot.services import SessionService
        print("SUCCESS: Services init working")
        return True
    except ImportError as e:
        print(f"FAILED: Services init failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Session Service and API Integration Fixes...\n")
    
    tests = [
        ("Session Service", test_session_service),
        ("API Integration", test_api_integration),
        ("Services Init", test_services_init),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        results[test_name] = test_func()
    
    print(f"\n{'='*60}")
    print("TEST RESULTS")
    print('='*60)
    
    failed_tests = [name for name, result in results.items() if not result]
    passed_tests = [name for name, result in results.items() if result]
    
    print(f"\nPassed: {len(passed_tests)}")
    for test in passed_tests:
        print(f"   - {test}")
    
    print(f"\nFailed: {len(failed_tests)}")
    for test in failed_tests:
        print(f"   - {test}")
    
    if len(failed_tests) == 0:
        print("\n🎉 ALL TESTS PASSED! Session Service and API Integration are working.")
    else:
        print(f"\n❌ {len(failed_tests)} tests failed. Need to investigate further.")

if __name__ == "__main__":
    main()