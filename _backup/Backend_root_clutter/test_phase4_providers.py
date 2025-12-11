#!/usr/bin/env python3
"""
Test Phase 4 Components: Provider Configuration
"""

import sys
import os
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_provider_service():
    """Test if provider service can be imported and initialized"""
    print("Testing Provider Service...")
    try:
        from backend_app.chatbot.services.provider_service import ProviderService
        print("SUCCESS: Provider Service imported successfully")
        
        # Test that enums are available
        from backend_app.chatbot.services.provider_service import (
            ProviderStatus, LoadBalanceStrategy, ProviderMetrics, ProviderConfig
        )
        print("   - ProviderStatus enum available")
        print("   - LoadBalanceStrategy enum available")
        print("   - ProviderMetrics dataclass available")
        print("   - ProviderConfig dataclass available")
        
        return True
    except ImportError as e:
        print(f"FAILED: Provider Service import failed: {e}")
        return False

def test_provider_service_methods():
    """Test Provider Service method signatures"""
    print("\nTesting Provider Service Methods...")
    try:
        from backend_app.chatbot.services.provider_service import ProviderService
        
        # Get method signatures
        methods = [
            'get_best_provider',
            'execute_with_fallback',
            'get_provider_metrics',
            'get_provider_status',
            'add_provider',
            'remove_provider',
            'update_provider_config',
            'shutdown'
        ]
        
        for method_name in methods:
            if hasattr(ProviderService, method_name):
                print(f"   - {method_name} [OK]")
            else:
                print(f"   - {method_name} [FAIL]")
                return False
        
        return True
    except Exception as e:
        print(f"FAILED: Provider Service methods test failed: {e}")
        return False

def test_services_integration():
    """Test if all services are properly integrated"""
    print("\nTesting Services Integration...")
    try:
        from backend_app.chatbot.services import (
            SessionService, ApplicationService, LLMService, 
            MessageRouter, SkillRegistry, MessageEngine, ProviderService
        )
        print("SUCCESS: All services can be imported including ProviderService")
        print("   - SessionService [OK]")
        print("   - ApplicationService [OK]")
        print("   - LLMService [OK]")
        print("   - MessageRouter [OK]")
        print("   - SkillRegistry [OK]")
        print("   - MessageEngine [OK]")
        print("   - ProviderService [OK]")
        return True
    except ImportError as e:
        print(f"FAILED: Services integration failed: {e}")
        return False

def test_config_integration():
    """Test if provider configuration is properly integrated"""
    print("\nTesting Config Integration...")
    try:
        from backend_app.config import settings
        
        # Test provider configuration fields
        provider_fields = [
            'ENABLE_PROVIDER_SYSTEM',
            'PRIMARY_PROVIDER',
            'SECONDARY_PROVIDER', 
            'FALLBACK_PROVIDER',
            'OPENROUTER_API_KEY',
            'GEMINI_API_KEY',
            'GROQ_API_KEY',
            'PROVIDER_TIMEOUT',
            'PROVIDER_RETRY_ATTEMPTS',
            'PROVIDER_LOAD_BALANCE'
        ]
        
        for field in provider_fields:
            if hasattr(settings, field):
                value = getattr(settings, field)
                print(f"   - {field}: {type(value).__name__} = {value}")
            else:
                print(f"   - {field}: ❌ Not found")
                return False
        
        return True
    except Exception as e:
        print(f"FAILED: Config integration test failed: {e}")
        return False

def test_provider_enums():
    """Test provider enums and dataclasses"""
    print("\nTesting Provider Enums...")
    try:
        from backend_app.chatbot.services.provider_service import (
            ProviderStatus, LoadBalanceStrategy
        )
        
        # Test ProviderStatus enum
        status_values = [status.value for status in ProviderStatus]
        print(f"   - ProviderStatus values: {status_values}")
        
        # Test LoadBalanceStrategy enum
        strategy_values = [strategy.value for strategy in LoadBalanceStrategy]
        print(f"   - LoadBalanceStrategy values: {strategy_values}")
        
        return True
    except Exception as e:
        print(f"FAILED: Provider enums test failed: {e}")
        return False

def main():
    """Run all Phase 4 tests"""
    print("Testing Phase 4 Components: Provider Configuration\n")
    
    tests = [
        ("Provider Service", test_provider_service),
        ("Provider Service Methods", test_provider_service_methods),
        ("Services Integration", test_services_integration),
        ("Config Integration", test_config_integration),
        ("Provider Enums", test_provider_enums),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        results[test_name] = test_func()
    
    print(f"\n{'='*60}")
    print("PHASE 4 TEST RESULTS")
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
        print("\nALL PHASE 4 TESTS PASSED!")
        print("Provider Configuration system is working and integrated.")
    else:
        print(f"\n{len(failed_tests)} tests failed. Need to investigate further.")
    
    print(f"\nPHASE 4 PROGRESS:")
    print(f"   - Provider Service: {'[OK]' if 'Provider Service' in passed_tests else '[FAIL]'}")
    print(f"   - Provider Configuration: {'[OK]' if 'Config Integration' in passed_tests else '[FAIL]'}")
    print(f"   - Service Integration: {'[OK]' if 'Services Integration' in passed_tests else '[FAIL]'}")

if __name__ == "__main__":
    main()