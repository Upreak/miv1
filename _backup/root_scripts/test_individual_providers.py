#!/usr/bin/env python3
"""
Test individual providers to identify which ones have working API keys
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the Backend directory to the path
sys.path.append('Backend')

from backend_app.brain_module.providers.provider_orchestrator import ProviderOrchestrator
from backend_app.brain_module.providers.provider_factory import create_provider_from_env
from backend_app.brain_module.utils.logger import get_logger

logger = get_logger("provider_test")

def load_env_vars():
    """Load environment variables from .env file"""
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print(f"[INFO] Environment variables loaded from {env_path}")
    else:
        print(f"[WARNING] .env file not found at {env_path}")

async def test_individual_provider(provider_name: str, provider_instance):
    """Test a single provider individually"""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name}")
    print(f"{'='*60}")
    
    try:
        # Test payload
        test_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Please respond with just 'OK' to test if this provider is working."
                }
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        print(f"[INFO] Testing {provider_name} with simple request...")
        
        # Make the API call (payload as positional argument)
        result = await provider_instance.generate(test_payload)
        
        if result.get("success"):
            print(f"[SUCCESS] {provider_name} is working!")
            print(f"[SUCCESS] Response: {result.get('text', 'No response')[:100]}...")
            print(f"[SUCCESS] Provider: {provider_instance.name}")
            print(f"[SUCCESS] Model: {provider_instance.model}")
            if result.get('usage'):
                print(f"[SUCCESS] Usage: {result.get('usage')}")
            return True
        else:
            error = result.get('error', 'Unknown error')
            print(f"[FAILED] {provider_name} failed: {error}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception testing {provider_name}: {str(e)}")
        return False

async def test_all_providers():
    """Test all providers individually"""
    print("Starting individual provider tests...")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load environment variables
    load_env_vars()
    
    # Test results
    results = {}
    
    # Test each provider slot (1-4)
    providers_to_test = [
        ("Provider 1 (OpenRouter)", 1),
        ("Provider 2 (Gemini)", 2),
        ("Provider 3 (Groq)", 3),
        ("Provider 4 (OpenRouter)", 4)
    ]
    
    for provider_name, slot_number in providers_to_test:
        try:
            # Create provider using factory with slot number
            provider = create_provider_from_env(slot_number)
            if provider:
                success = await test_individual_provider(provider_name, type(provider))
                results[provider_name] = success
            else:
                print(f"[WARNING] Could not create {provider_name} - missing configuration")
                results[provider_name] = False
        except Exception as e:
            print(f"[ERROR] Failed to test {provider_name}: {str(e)}")
            results[provider_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("PROVIDER TEST SUMMARY")
    print(f"{'='*60}")
    
    working_providers = [name for name, success in results.items() if success]
    failed_providers = [name for name, success in results.items() if not success]
    
    print(f"[INFO] Total providers tested: {len(results)}")
    print(f"[SUCCESS] Working providers: {len(working_providers)}")
    print(f"[FAILED] Failed providers: {len(failed_providers)}")
    
    if working_providers:
        print(f"\n[WORKING] {', '.join(working_providers)}")
    
    if failed_providers:
        print(f"\n[FAILED] {', '.join(failed_providers)}")
    
    # Save results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"provider_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            "test_time": datetime.now().isoformat(),
            "results": results,
            "working_providers": working_providers,
            "failed_providers": failed_providers
        }, f, indent=2)
    
    print(f"\n[INFO] Detailed results saved to: {filename}")
    
    return results

async def main():
    """Main test function"""
    print("Individual Provider Test")
    print("=" * 60)
    
    try:
        results = await test_all_providers()
        
        print(f"\n{'='*60}")
        print("TEST COMPLETED")
        print(f"{'='*60}")
        
        working_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        if working_count > 0:
            print(f"[SUCCESS] {working_count}/{total_count} providers are working")
            print("[INFO] The Brain Module should work with these providers")
        else:
            print("[ERROR] No providers are working")
            print("[INFO] Check API keys in .env file or wait for rate limits to reset")
        
        return results
        
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        return None

if __name__ == "__main__":
    results = asyncio.run(main())