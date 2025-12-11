#!/usr/bin/env python3
"""
Quick verification script to check if all chatbot components are working
"""

import sys
import os

# Add the backend app to Python path
sys.path.insert(0, 'backend_app')

def test_imports():
    """Test all critical imports"""
    print("Testing Critical Imports...")
    
    try:
        # Core chatbot components
        from backend_app.chatbot.controller import ChatbotController
        from backend_app.chatbot.services.session_service import SessionService
        from backend_app.chatbot.services.provider_service import ProviderService
        from backend_app.chatbot.services.message_engine import MessageEngine
        print("SUCCESS: Core chatbot components imported successfully")
        
        # Telegram integration (without config)
        from backend_app.services.telegram_service import telegram_bot_service
        print("SUCCESS: Telegram service imported successfully")
        
        # API endpoints
        from backend_app.api.v1 import chatbot, telegram
        print("SUCCESS: API endpoints imported successfully")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Import failed: {e}")
        return False

def test_dependencies():
    """Test key dependencies"""
    print("\nTesting Dependencies...")
    
    try:
        import fastapi
        print(f"SUCCESS: FastAPI: {fastapi.__version__}")
        
        import sqlalchemy
        print(f"SUCCESS: SQLAlchemy: {sqlalchemy.__version__}")
        
        import asyncpg
        print(f"SUCCESS: asyncpg: {asyncpg.__version__}")
        
        import httpx
        print(f"SUCCESS: httpx: {httpx.__version__}")
        
        import pydantic
        print(f"SUCCESS: Pydantic: {pydantic.VERSION}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Dependency test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("CHATBOT SYSTEM VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Dependencies Test", test_dependencies)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append(result)
    
    # Summary
    total_tests = len(tests)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY:")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\nALL TESTS PASSED!")
        print("SUCCESS: Your chatbot system is ready for deployment!")
        print("Run: python scripts/deploy_telegram_bot.py")
        return 0
    else:
        print(f"\nERROR: {failed_tests} test(s) failed.")
        print("WARNING: Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())