#!/usr/bin/env python3
"""
Simple Chatbot System Test
Basic validation without complex dependencies
"""

import sys
import logging

# Configure logging to avoid Unicode issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    
    try:
        # Test chatbot controller
        from backend_app.chatbot.controller import ChatbotController
        print("✓ ChatbotController imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ChatbotController: {e}")
        return False
    
    try:
        # Test skills
        from backend_app.chatbot.services.skills.onboarding_skill import OnboardingSkill
        print("✓ OnboardingSkill imported successfully")
    except Exception as e:
        print(f"✗ Failed to import OnboardingSkill: {e}")
        return False
    
    try:
        from backend_app.chatbot.services.skills.resume_intake_skill import ResumeIntakeSkill
        print("✓ ResumeIntakeSkill imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ResumeIntakeSkill: {e}")
        return False
    
    try:
        # Test enums
        from backend_app.chatbot.models.session_model import UserRole, ConversationState
        print("✓ Enums imported successfully")
    except Exception as e:
        print(f"✗ Failed to import enums: {e}")
        return False
    
    try:
        # Test API routes
        from backend_app.api.v1 import chatbot
        print("✓ Chatbot API routes imported successfully")
    except Exception as e:
        print(f"✗ Failed to import chatbot API: {e}")
        return False
    
    try:
        from backend_app.api.v1 import whatsapp
        print("✓ WhatsApp API routes imported successfully")
    except Exception as e:
        print(f"✗ Failed to import WhatsApp API: {e}")
        return False
    
    try:
        from backend_app.api.v1 import telegram
        print("✓ Telegram API routes imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Telegram API: {e}")
        return False
    
    return True


def test_skill_registry():
    """Test skill registry functionality"""
    print("\nTesting skill registry...")
    
    try:
        from backend_app.chatbot.skill_registry import (
            get_skill_registry,
            initialize_chatbot_system
        )
        
        # Initialize system
        success = initialize_chatbot_system()
        if success:
            print("✓ Chatbot system initialized successfully")
        else:
            print("✗ Failed to initialize chatbot system")
            return False
        
        # Get skill registry
        registry = get_skill_registry()
        if registry:
            skills = registry.get_all()
            print(f"✓ Found {len(skills)} registered skills: {[skill.name for skill in skills]}")
        else:
            print("✗ Could not get skill registry")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Skill registry test failed: {e}")
        return False


def test_controller_creation():
    """Test controller creation"""
    print("\nTesting controller creation...")
    
    try:
        from backend_app.chatbot.controller import ChatbotController
        
        # Create controller (this tests all dependencies)
        controller = ChatbotController()
        print("✓ ChatbotController created successfully")
        
        # Check methods
        methods = ['start_session', 'process_message', 'get_session', 'update_session_state']
        for method in methods:
            if hasattr(controller, method):
                print(f"✓ Controller has {method} method")
            else:
                print(f"✗ Controller missing {method} method")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Controller creation failed: {e}")
        return False


def main():
    """Main test function"""
    print("="*60)
    print("SIMPLE CHATBOT SYSTEM TEST")
    print("="*60)
    
    tests = [
        ("Import Test", test_imports),
        ("Skill Registry Test", test_skill_registry),
        ("Controller Creation Test", test_controller_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append(False)
    
    # Summary
    total_tests = len(tests)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! Chatbot system components are working.")
        return 0
    else:
        print(f"\n❌ {failed_tests} test(s) failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Test suite failed with exception: {e}")
        sys.exit(1)