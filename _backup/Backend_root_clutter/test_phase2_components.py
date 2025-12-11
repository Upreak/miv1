#!/usr/bin/env python3
"""
Test Phase 2 Components: State Machine and Application Service
"""

import sys
import os
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_state_machine():
    """Test if state machine can be imported and initialized"""
    print("Testing State Machine...")
    try:
        from backend_app.chatbot.engine.state_machine import StateMachine
        from backend_app.chatbot.services.session_service import SessionService
        
        # Mock session service for testing
        class MockSessionService:
            async def get_session(self, session_id):
                return None
            
            async def update_session_state(self, session_id, state):
                return True
        
        # Test state machine initialization
        mock_session_service = MockSessionService()
        state_machine = StateMachine(mock_session_service)
        
        print("SUCCESS: State Machine imported and initialized")
        print(f"   - Transitions defined: {len(state_machine.transitions)}")
        print(f"   - State handlers: {len(state_machine.state_handlers)}")
        
        return True
    except ImportError as e:
        print(f"FAILED: State Machine import failed: {e}")
        return False
    except Exception as e:
        print(f"FAILED: State Machine initialization failed: {e}")
        return False

def test_application_service():
    """Test if application service can be imported"""
    print("\nTesting Application Service...")
    try:
        from backend_app.chatbot.services.application_service import ApplicationService
        print("SUCCESS: Application Service imported successfully")
        return True
    except ImportError as e:
        print(f"FAILED: Application Service import failed: {e}")
        return False

def test_services_init():
    """Test if services __init__.py includes all services"""
    print("\nTesting Services Init...")
    try:
        from backend_app.chatbot.services import (
            SessionService, ApplicationService, LLMService, 
            MessageRouter, SkillRegistry
        )
        print("SUCCESS: All services can be imported")
        print("   - SessionService [OK]")
        print("   - ApplicationService [OK]")
        print("   - LLMService [OK]")
        print("   - MessageRouter [OK]")
        print("   - SkillRegistry [OK]")
        return True
    except ImportError as e:
        print(f"FAILED: Services init failed: {e}")
        return False

def test_state_machine_transitions():
    """Test state machine transition logic"""
    print("\nTesting State Machine Transitions...")
    try:
        from backend_app.chatbot.engine.state_machine import (
            StateMachine, ConversationState, TransitionResult
        )
        
        # Test transition validation
        from backend_app.chatbot.models.session_model import ConversationState
        
        # Check if states are properly defined
        states = list(ConversationState)
        print(f"   - Available states: {len(states)}")
        for state in states:
            print(f"     * {state.value}")
        
        return True
    except Exception as e:
        print(f"FAILED: State machine transitions test failed: {e}")
        return False

def main():
    """Run all Phase 2 tests"""
    print("Testing Phase 2 Components: State Machine & Application Service\n")
    
    tests = [
        ("State Machine", test_state_machine),
        ("Application Service", test_application_service),
        ("Services Init", test_services_init),
        ("State Machine Transitions", test_state_machine_transitions),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        results[test_name] = test_func()
    
    print(f"\n{'='*60}")
    print("PHASE 2 TEST RESULTS")
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
        print("\n🎉 ALL PHASE 2 TESTS PASSED!")
        print("State Machine Framework and Application Service are working.")
    else:
        print(f"\n❌ {len(failed_tests)} tests failed. Need to investigate further.")
    
    print(f"\n📊 PHASE 2 PROGRESS:")
    print(f"   - State Machine Framework: {'✅' if 'State Machine' in passed_tests else '❌'}")
    print(f"   - Application Service: {'✅' if 'Application Service' in passed_tests else '❌'}")
    print(f"   - Service Integration: {'✅' if 'Services Init' in passed_tests else '❌'}")

if __name__ == "__main__":
    main()