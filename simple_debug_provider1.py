#!/usr/bin/env python3
"""
Simple debug script to test provider1 (OpenRouter) without Unicode characters
"""

import os
import json
import time
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add Backend to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from backend_app.brain_module.providers.provider_usage import ProviderUsageManager
from backend_app.brain_module.providers.provider_factory import create_provider_from_env
from backend_app.brain_module.utils.time_utils import now_ts, today_date_str

def check_provider1_config():
    """Check provider1 configuration from environment"""
    print("=" * 60)
    print("PROVIDER1 CONFIGURATION CHECK")
    print("=" * 60)
    
    provider_type = os.getenv("PROVIDER1_TYPE", "")
    provider_key = os.getenv("PROVIDER1_KEY", "")
    provider_model = os.getenv("PROVIDER1_MODEL", "")
    provider_baseurl = os.getenv("PROVIDER1_BASEURL", "")
    
    print(f"PROVIDER1_TYPE: {provider_type}")
    print(f"PROVIDER1_KEY: {'*' * 40 if provider_key else 'NOT SET'}")
    print(f"PROVIDER1_MODEL: {provider_model}")
    print(f"PROVIDER1_BASEURL: {provider_baseurl}")
    
    # Check if key looks valid (basic format check)
    if provider_key and provider_key.startswith('sk-or-'):
        print("SUCCESS: Key format appears valid (OpenRouter format)")
    elif provider_key:
        print("WARNING: Key format may be incorrect")
    else:
        print("ERROR: Key not set")
    
    return {
        "type": provider_type,
        "has_key": bool(provider_key),
        "model": provider_model,
        "baseurl": provider_baseurl
    }

def check_provider1_state():
    """Check provider1 usage state"""
    print("\n" + "=" * 60)
    print("PROVIDER1 USAGE STATE")
    print("=" * 60)
    
    usage = ProviderUsageManager()
    provider_id = "provider1_openrouter"
    
    current_time = now_ts()
    state = usage.get_state(provider_id)
    
    print(f"Provider ID: {provider_id}")
    print(f"Date: {state.get('date')}")
    print(f"Count: {state.get('count')}")
    print(f"Current Timestamp: {current_time}")
    print(f"Cooldown Until: {state.get('cooldown_until')}")
    print(f"Cooldown Until (readable): {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(state.get('cooldown_until', 0)))}")
    
    # Check cooldown status
    cooldown_until = state.get('cooldown_until', 0)
    if cooldown_until > current_time:
        cooldown_remaining = cooldown_until - current_time
        print("ERROR: PROVIDER1 IS IN COOLDOWN")
        print(f"   Remaining cooldown: {cooldown_remaining} seconds ({cooldown_remaining/3600:.1f} hours)")
    else:
        print("SUCCESS: PROVIDER1 IS OUT OF COOLDOWN")
    
    # Check daily limit
    daily_limit = int(os.getenv("BRAIN_PROVIDER_DAILY_LIMIT", "1000"))
    current_count = state.get('count', 0)
    if current_count >= daily_limit:
        print(f"ERROR: DAILY LIMIT REACHED: {current_count}/{daily_limit}")
    else:
        remaining = daily_limit - current_count
        print(f"SUCCESS: DAILY LIMIT OK: {current_count}/{daily_limit} ({remaining} remaining)")
    
    return state

def test_direct_provider_creation():
    """Test creating provider1 instance directly"""
    print("\n" + "=" * 60)
    print("DIRECT PROVIDER CREATION TEST")
    print("=" * 60)
    
    try:
        provider = create_provider_from_env(1)
        if provider:
            print(f"SUCCESS: Provider created successfully")
            print(f"   Name: {provider.name}")
            print(f"   Model: {provider.model}")
            print(f"   Type: {type(provider).__name__}")
            return provider
        else:
            print("ERROR: Failed to create provider (configuration issue)")
            return None
    except Exception as e:
        print(f"ERROR: Exception during provider creation: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_simple_request(provider):
    """Test provider with simple 'hi' message"""
    print("\n" + "=" * 60)
    print("SIMPLE REQUEST TEST ('hi')")
    print("=" * 60)
    
    if not provider:
        print("ERROR: No provider to test")
        return None
    
    # Simple test payload
    test_payload = {
        "messages": [
            {"role": "user", "content": "hi"}
        ]
    }
    
    try:
        print("Sending test request to provider...")
        print(f"Provider: {provider.name}")
        print(f"Model: {provider.model}")
        print(f"Payload: {test_payload}")
        
        start_time = time.time()
        result = provider.generate(test_payload, timeout=30)
        end_time = time.time()
        
        print(f"SUCCESS: Request completed in {end_time - start_time:.2f} seconds")
        print(f"Result: {result}")
        
        if result.get("success"):
            print("SUCCESS: Provider responded correctly")
            print(f"Response: {result.get('text', 'No text')}")
        else:
            print("ERROR: Provider returned error")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"ERROR: EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("COMPREHENSIVE PROVIDER1 DEBUG ANALYSIS")
    print("=" * 60)
    
    # 1. Check configuration
    config = check_provider1_config()
    
    # 2. Check usage state
    state = check_provider1_state()
    
    # 3. Test direct provider creation
    provider = test_direct_provider_creation()
    
    # 4. Test simple request if provider created
    if provider:
        test_result = test_simple_request(provider)
    else:
        test_result = None
    
    # 5. Summary
    print("\n" + "=" * 60)
    print("DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    current_time = now_ts()
    cooldown_until = state.get('cooldown_until', 0)
    
    if cooldown_until > current_time:
        print("PRIMARY ISSUE: PROVIDER IS IN COOLDOWN")
        print(f"   Cooldown until: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cooldown_until))}")
        print(f"   This was likely caused by previous API failures")
    else:
        print("PROVIDER IS OUT OF COOLDOWN - should be available")
    
    if config.get("has_key"):
        print("API key is configured")
    else:
        print("API key is missing")
    
    if provider:
        print("Provider instance can be created")
    else:
        print("Provider instance creation failed")
    
    if test_result and test_result.get("success"):
        print("Provider responds to simple requests")
    elif test_result:
        print("Provider fails on simple requests")
    else:
        print("Could not test provider response")
    
    print("\nRECOMMENDED ACTIONS:")
    if cooldown_until > current_time:
        print("1. Wait for cooldown to expire or clear the cooldown state")
    if not config.get("has_key"):
        print("2. Check PROVIDER1_KEY environment variable")
    if not provider:
        print("3. Check provider configuration and dependencies")
    if test_result and not test_result.get("success"):
        print("4. Fix the API parameter issue in openrouter_provider.py")

if __name__ == "__main__":
    main()