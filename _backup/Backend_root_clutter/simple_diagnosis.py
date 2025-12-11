#!/usr/bin/env python3
"""
Simple Chatbot Diagnosis Script
Tests the most critical components to identify root causes
"""

import sys
import os
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_session_service():
    """Test if session service exists and can be imported"""
    print("Testing Session Service...")
    try:
        from chatbot.services.session_service import SessionService
        print("SUCCESS: Session Service imported")
        return True
    except ImportError as e:
        print(f"FAILED: Session Service import failed: {e}")
        return False

def test_api_integration():
    """Test if chatbot API is properly integrated"""
    print("\nTesting API Integration...")
    try:
        from api.v1 import chatbot
        print("SUCCESS: Chatbot API module imported")
        
        # Check if endpoints exist
        endpoints = [attr for attr in dir(chatbot) if attr.startswith('_') is False]
        print(f"Available endpoints: {endpoints}")
        return True
    except ImportError as e:
        print(f"FAILED: API Integration failed: {e}")
        return False

def test_state_machine():
    """Test state machine implementation"""
    print("\nTesting State Machine...")
    try:
        from chatbot.state_manager import StateManager
        state_manager = StateManager()
        print("SUCCESS: Basic StateManager imported")
        
        # Check for actual state machine
        try:
            from chatbot.engine.state_machine import StateMachine
            print("SUCCESS: Full State Machine found")
            return True
        except ImportError:
            print("WARNING: Only basic state manager found, no full state machine")
            return False
    except ImportError as e:
        print(f"FAILED: State Machine import failed: {e}")
        return False

def test_prescreen_engine():
    """Test prescreen engine implementation"""
    print("\nTesting Prescreen Engine...")
    try:
        from chatbot.prescreening_service import PrescreeningService
        service = PrescreeningService()
        print("SUCCESS: Prescreening Service imported")
        
        # Check methods
        methods = [method for method in dir(service) if not method.startswith('_')]
        print(f"Available methods: {methods}")
        return True
    except ImportError as e:
        print(f"FAILED: Prescreening Service import failed: {e}")
        return False

def test_application_service():
    """Test application service integration"""
    print("\nTesting Application Service...")
    try:
        from chatbot.services.application_service import ApplicationService
        print("SUCCESS: Application Service imported")
        return True
    except ImportError as e:
        print(f"FAILED: Application Service import failed: {e}")
        return False

def test_database_models():
    """Test database models"""
    print("\nTesting Database Models...")
    try:
        from db.models import Session, MessageLog
        print("SUCCESS: Chatbot models imported")
        return True
    except ImportError as e:
        print(f"FAILED: Database models import failed: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("Starting Chatbot Diagnosis...\n")
    
    tests = [
        ("Session Service", test_session_service),
        ("API Integration", test_api_integration),
        ("State Machine", test_state_machine),
        ("Prescreen Engine", test_prescreen_engine),
        ("Application Service", test_application_service),
        ("Database Models", test_database_models),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        results[test_name] = test_func()
    
    print(f"\n{'='*60}")
    print("DIAGNOSIS SUMMARY")
    print('='*60)
    
    failed_tests = [name for name, result in results.items() if not result]
    passed_tests = [name for name, result in results.items() if result]
    
    print(f"\nPassed: {len(passed_tests)}")
    for test in passed_tests:
        print(f"   - {test}")
    
    print(f"\nFailed: {len(failed_tests)}")
    for test in failed_tests:
        print(f"   - {test}")
    
    print(f"\nCRITICAL ISSUES IDENTIFIED:")
    if "Session Service" in failed_tests:
        print("   1. Session Service is missing - CRITICAL")
    if "API Integration" in failed_tests:
        print("   2. API Integration is broken - CRITICAL")
    if "State Machine" in failed_tests:
        print("   3. Full State Machine not implemented")
    if "Application Service" in failed_tests:
        print("   4. Application Service missing")
    
    print(f"\nRECOMMENDED ACTIONS:")
    if "Session Service" in failed_tests:
        print("   1. Create Session Service implementation")
    if "API Integration" in failed_tests:
        print("   2. Fix API router integration")
    if "State Machine" in failed_tests:
        print("   3. Implement full state machine framework")
    if "Application Service" in failed_tests:
        print("   4. Create Application Service")

if __name__ == "__main__":
    main()