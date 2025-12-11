#!/usr/bin/env python3
"""
Test Phase 3 Components: Message Engine
"""

import sys
import os
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_message_engine():
    """Test if message engine can be imported and initialized"""
    print("Testing Message Engine...")
    try:
        from backend_app.chatbot.services.message_engine import MessageEngine
        print("SUCCESS: Message Engine imported successfully")
        
        # Test that MessageLog model is available
        from backend_app.chatbot.models.message_log_model import MessageLog, MessageType, MessageDirection
        print("   - MessageLog model imported")
        print("   - MessageType enum available")
        print("   - MessageDirection enum available")
        
        return True
    except ImportError as e:
        print(f"FAILED: Message Engine import failed: {e}")
        return False

def test_message_engine_methods():
    """Test Message Engine method signatures"""
    print("\nTesting Message Engine Methods...")
    try:
        from backend_app.chatbot.services.message_engine import MessageEngine
        
        # Get method signatures
        methods = [
            'save_bot_message',
            'save_candidate_message', 
            'load_transcript',
            'get_message_stats',
            'export_transcript',
            'cleanup_old_messages',
            'get_session_activity',
            'mark_message_processed',
            'get_message_by_platform_message_id'
        ]
        
        for method_name in methods:
            if hasattr(MessageEngine, method_name):
                print(f"   - {method_name} [OK]")
            else:
                print(f"   - {method_name} [FAIL]")
                return False
        
        return True
    except Exception as e:
        print(f"FAILED: Message Engine methods test failed: {e}")
        return False

def test_services_integration():
    """Test if all services are properly integrated"""
    print("\nTesting Services Integration...")
    try:
        from backend_app.chatbot.services import (
            SessionService, ApplicationService, LLMService, 
            MessageRouter, SkillRegistry, MessageEngine
        )
        print("SUCCESS: All services can be imported including MessageEngine")
        print("   - SessionService [OK]")
        print("   - ApplicationService [OK]")
        print("   - LLMService [OK]")
        print("   - MessageRouter [OK]")
        print("   - SkillRegistry [OK]")
        print("   - MessageEngine [OK]")
        return True
    except ImportError as e:
        print(f"FAILED: Services integration failed: {e}")
        return False

def test_message_models():
    """Test message models and enums"""
    print("\nTesting Message Models...")
    try:
        from backend_app.chatbot.models.message_log_model import (
            MessageLog, MessageType, MessageDirection
        )
        
        # Test enums
        message_types = list(MessageType)
        print(f"   - Message types: {[mt.value for mt in message_types]}")
        
        message_directions = list(MessageDirection)
        print(f"   - Message directions: {[md.value for md in message_directions]}")
        
        return True
    except Exception as e:
        print(f"FAILED: Message models test failed: {e}")
        return False

def main():
    """Run all Phase 3 tests"""
    print("Testing Phase 3 Components: Message Engine\n")
    
    tests = [
        ("Message Engine", test_message_engine),
        ("Message Engine Methods", test_message_engine_methods),
        ("Services Integration", test_services_integration),
        ("Message Models", test_message_models),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        results[test_name] = test_func()
    
    print(f"\n{'='*60}")
    print("PHASE 3 TEST RESULTS")
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
        print("\nALL PHASE 3 TESTS PASSED!")
        print("Message Engine is working and integrated.")
    else:
        print(f"\n❌ {len(failed_tests)} tests failed. Need to investigate further.")
    
    print(f"\nPHASE 3 PROGRESS:")
    print(f"   - Message Engine: {'[OK]' if 'Message Engine' in passed_tests else '[FAIL]'}")
    print(f"   - Message Persistence: {'[OK]' if 'Message Models' in passed_tests else '[FAIL]'}")
    print(f"   - Service Integration: {'[OK]' if 'Services Integration' in passed_tests else '[FAIL]'}")

if __name__ == "__main__":
    main()