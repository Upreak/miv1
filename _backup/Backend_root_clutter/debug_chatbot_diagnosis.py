#!/usr/bin/env python3
"""
Chatbot Diagnosis Script
Tests the most critical components to identify root causes
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent / "Backend"
sys.path.insert(0, str(backend_path))

async def test_session_service():
    """Test if session service exists and can be imported"""
    print("🔍 Testing Session Service...")
    try:
        from backend_app.chatbot.services.session_service import SessionService
        print("✅ Session Service imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Session Service import failed: {e}")
        return False

async def test_api_integration():
    """Test if chatbot API is properly integrated"""
    print("\n🔍 Testing API Integration...")
    try:
        from backend_app.api.v1 import chatbot
        print("✅ Chatbot API module imported")
        
        # Check if endpoints exist
        endpoints = [attr for attr in dir(chatbot) if attr.startswith('_') is False]
        print(f"   Available endpoints: {endpoints}")
        return True
    except ImportError as e:
        print(f"❌ API Integration failed: {e}")
        return False

async def test_state_machine():
    """Test state machine implementation"""
    print("\n🔍 Testing State Machine...")
    try:
        from backend_app.chatbot.state_manager import StateManager
        state_manager = StateManager()
        print("✅ Basic StateManager imported")
        
        # Test if it has state transition methods
        methods = [method for method in dir(state_manager) if 'state' in method.lower()]
        print(f"   State-related methods: {methods}")
        
        # Check for actual state machine
        try:
            from backend_app.chatbot.engine.state_machine import StateMachine
            print("✅ Full State Machine found")
            return True
        except ImportError:
            print("⚠️  Only basic state manager found, no full state machine")
            return False
    except ImportError as e:
        print(f"❌ State Machine import failed: {e}")
        return False

async def test_prescreen_engine():
    """Test prescreen engine implementation"""
    print("\n🔍 Testing Prescreen Engine...")
    try:
        from backend_app.chatbot.prescreening_service import PrescreeningService
        service = PrescreeningService()
        print("✅ Prescreening Service imported")
        
        # Check methods
        methods = [method for method in dir(service) if not method.startswith('_')]
        print(f"   Available methods: {methods}")
        return True
    except ImportError as e:
        print(f"❌ Prescreening Service import failed: {e}")
        return False

async def test_application_service():
    """Test application service integration"""
    print("\n🔍 Testing Application Service...")
    try:
        from backend_app.chatbot.services.application_service import ApplicationService
        print("✅ Application Service imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Application Service import failed: {e}")
        return False

async def test_provider_configuration():
    """Test provider configuration"""
    print("\n🔍 Testing Provider Configuration...")
    try:
        from backend_app.brain_module.providers.provider_factory import create_provider_from_env
        provider = create_provider_from_env(0)
        if provider:
            print("✅ Provider factory working")
            return True
        else:
            print("⚠️  Provider factory returned None")
            return False
    except ImportError as e:
        print(f"❌ Provider configuration failed: {e}")
        return False

async def test_database_models():
    """Test database models"""
    print("\n🔍 Testing Database Models...")
    try:
        from backend_app.db.models import Session, MessageLog
        print("✅ Chatbot models imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Database models import failed: {e}")
        return False

async def main():
    """Run all diagnostic tests"""
    print("🚀 Starting Chatbot Diagnosis...\n")
    
    tests = [
        ("Session Service", test_session_service),
        ("API Integration", test_api_integration),
        ("State Machine", test_state_machine),
        ("Prescreen Engine", test_prescreen_engine),
        ("Application Service", test_application_service),
        ("Provider Configuration", test_provider_configuration),
        ("Database Models", test_database_models),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        results[test_name] = await test_func()
    
    print(f"\n{'='*60}")
    print("DIAGNOSIS SUMMARY")
    print('='*60)
    
    failed_tests = [name for name, result in results.items() if not result]
    passed_tests = [name for name, result in results.items() if result]
    
    print(f"\n✅ Passed: {len(passed_tests)}")
    for test in passed_tests:
        print(f"   • {test}")
    
    print(f"\n❌ Failed: {len(failed_tests)}")
    for test in failed_tests:
        print(f"   • {test}")
    
    print(f"\n🎯 CRITICAL ISSUES IDENTIFIED:")
    if "Session Service" in failed_tests:
        print("   1. Session Service is missing - CRITICAL")
    if "API Integration" in failed_tests:
        print("   2. API Integration is broken - CRITICAL")
    if "State Machine" in failed_tests:
        print("   3. Full State Machine not implemented")
    if "Application Service" in failed_tests:
        print("   4. Application Service missing")
    
    print(f"\n💡 RECOMMENDED ACTIONS:")
    if "Session Service" in failed_tests:
        print("   1. Create Session Service implementation")
    if "API Integration" in failed_tests:
        print("   2. Fix API router integration")
    if "State Machine" in failed_tests:
        print("   3. Implement full state machine framework")
    if "Application Service" in failed_tests:
        print("   4. Create Application Service")

if __name__ == "__main__":
    asyncio.run(main())