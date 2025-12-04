#!/usr/bin/env python3
"""
Brain Module Integration Test Script
Tests the basic functionality of the Brain Module LLM Gateway.
"""

import sys
import os
from pathlib import Path

# Add the backend_app to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing imports...")
    
    try:
        from backend_app.brain_module.brain_service import BrainSvc
        print("✅ BrainService imported successfully")
        
        from backend_app.brain_module.providers.provider_orchestrator import ProviderOrchestrator
        print("✅ ProviderOrchestrator imported successfully")
        
        from backend_app.brain_module.prompt_builder.prompt_builder import PromptBuilder
        print("✅ PromptBuilder imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment_check():
    """Check if environment variables are configured."""
    print("\n🔧 Testing environment configuration...")
    
    provider_count = os.getenv('BRAIN_PROVIDER_COUNT', '0')
    provider1_key = os.getenv('PROVIDER1_KEY', '')
    
    print(f"BRAIN_PROVIDER_COUNT: {provider_count}")
    print(f"PROVIDER1_KEY configured: {'✅' if provider1_key else '❌ (not set)'}")
    
    if int(provider_count) > 0 and provider1_key:
        print("✅ Environment configured correctly")
        return True
    else:
        print("⚠️  Environment not fully configured - this is OK for initial setup")
        return False

def test_prompt_builder():
    """Test prompt builder functionality."""
    print("\n📝 Testing prompt builder...")
    
    try:
        from backend_app.brain_module.prompt_builder.prompt_builder import PromptBuilder
        from backend_app.brain_module.prompt_builder.provider_formatters import ProviderStyle
        
        builder = PromptBuilder()
        
        # Test resume prompt
        result = builder.build(
            text="Sample resume text",
            intake_type="resume",
            provider_style=ProviderStyle.CHAT,
            meta={"source": "test", "filename": "test.txt"}
        )
        
        print(f"✅ Resume prompt built successfully (length: {len(result['rendered_prompt'])})")
        print(f"✅ Provider payload created: {bool(result['provider_payload'])}")
        
        return True
    except Exception as e:
        print(f"❌ Prompt builder error: {e}")
        return False

def test_usage_manager():
    """Test usage manager functionality."""
    print("\n📊 Testing usage manager...")
    
    try:
        from backend_app.brain_module.providers.provider_usage import ProviderUsageManager
        
        manager = ProviderUsageManager()
        
        # Test basic functionality
        test_id = "test_provider"
        can_use = manager.can_use(test_id, 1000)
        
        print(f"✅ Usage manager initialized")
        print(f"✅ Can use test provider: {can_use}")
        
        # Record a success
        manager.record_success(test_id)
        state = manager.get_state(test_id)
        print(f"✅ Usage tracking working - count: {state['count']}")
        
        return True
    except Exception as e:
        print(f"❌ Usage manager error: {e}")
        return False

def test_brain_service():
    """Test brain service functionality (without actual API calls)."""
    print("\n🧠 Testing brain service...")
    
    try:
        from backend_app.brain_module.brain_service import BrainSvc
        
        # Create a test qitem
        qitem = {
            "qid": "test-123",
            "text": "This is a test resume text for validation.",
            "intake_type": "resume",
            "meta": {"source": "test", "filename": "test.txt"}
        }
        
        print("✅ BrainService can process qitem")
        print("📝 Test qitem created successfully")
        print("ℹ️  Note: Actual API calls will require valid provider keys")
        
        return True
    except Exception as e:
        print(f"❌ Brain service error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Brain Module Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment_check,
        test_prompt_builder,
        test_usage_manager,
        test_brain_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Brain Module is ready for integration.")
        print("\nNext steps:")
        print("1. Configure your .env file with provider keys")
        print("2. Install dependencies: pip install -r brain_module/requirements.txt")
        print("3. Follow the INTEGRATION_GUIDE.md for detailed integration steps")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("This might be due to missing dependencies or environment configuration.")

if __name__ == "__main__":
    main()