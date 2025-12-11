#!/usr/bin/env python3
"""
Final diagnosis script to identify the exact cause of "All providers failed"
"""

import os
import json
import time
from datetime import datetime

# Add Backend to path
import sys
sys.path.append('Backend/backend_app')

from brain_module.providers.provider_orchestrator import ProviderOrchestrator
from brain_module.providers.provider_usage import ProviderUsageManager
from brain_module.utils.logger import get_logger

logger = get_logger("final_diagnosis")

def main():
    print("=" * 60)
    print("FINAL DIAGNOSIS: Brain Module 'All providers failed'")
    print("=" * 60)
    
    # Check current time
    current_timestamp = int(time.time())
    current_time = datetime.fromtimestamp(current_timestamp)
    print(f"Current Time: {current_time} (timestamp: {current_timestamp})")
    print()
    
    # Load provider orchestrator
    try:
        orchestrator = ProviderOrchestrator()
        print(f"✅ Provider Orchestrator loaded successfully")
        print(f"Total providers configured: {len(orchestrator.providers)}")
        print()
        
        # Check each provider status
        print("PROVIDER STATUS ANALYSIS:")
        print("-" * 40)
        
        all_available = True
        for provider in orchestrator.providers:
            slot = provider["slot"]
            provider_id = f"provider{slot}_{provider['type']}"
            provider_name = provider["type"]
            model = provider["model"]
            
            print(f"Provider {slot} ({provider_name}):")
            print(f"  Model: {model}")
            print(f"  ID: {provider_id}")
            
            # Check usage status
            usage_status = orchestrator.usage.get_usage_state(provider_id)
            if usage_status:
                cooldown_until = usage_status.get("cooldown_until", 0)
                count = usage_status.get("count", 0)
                
                if cooldown_until > current_timestamp:
                    cooldown_remaining = cooldown_until - current_timestamp
                    cooldown_hours = cooldown_remaining // 3600
                    cooldown_minutes = (cooldown_remaining % 3600) // 60
                    print(f"  Status: ❌ COOLDOWN (expires in {cooldown_hours}h {cooldown_minutes}m)")
                    print(f"  Usage count: {count}")
                    all_available = False
                else:
                    print(f"  Status: ✅ AVAILABLE")
                    print(f"  Usage count: {count}")
            else:
                print(f"  Status: ❓ NO USAGE DATA")
                all_available = False
            
            print()
        
        # Check usage state file
        print("USAGE STATE FILE:")
        print("-" * 40)
        usage_file = "Backend/backend_app/brain_module/providers/provider_usage_state.json"
        if os.path.exists(usage_file):
            with open(usage_file, 'r') as f:
                usage_data = json.load(f)
                print(f"File exists with {len(usage_data)} providers")
                
                for provider_id, state in usage_data.items():
                    cooldown_until = state.get("cooldown_until", 0)
                    if cooldown_until > current_timestamp:
                        remaining = cooldown_until - current_timestamp
                        hours = remaining // 3600
                        minutes = (remaining % 3600) // 60
                        print(f"  {provider_id}: COOLDOWN ({hours}h {minutes}m remaining)")
                    else:
                        print(f"  {provider_id}: AVAILABLE")
        else:
            print(f"❌ File not found")
        
        print()
        
        # ROOT CAUSE ANALYSIS
        print("ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        if all_available:
            print("✅ ALL PROVIDERS ARE AVAILABLE")
            print("The Brain Module should work correctly.")
            print("If you're still getting 'All providers failed', check:")
            print("1. API key validity")
            print("2. Network connectivity")
            print("3. Provider service status")
        else:
            print("❌ SOME PROVIDERS ARE IN COOLDOWN")
            print("This explains the 'All providers failed' error.")
            print()
            print("SOLUTIONS:")
            print("1. WAIT for cooldown periods to expire")
            print("2. REFRESH API keys if they're invalid/expired")
            print("3. CHECK network connectivity")
            print("4. VERIFY provider service status")
        
        print()
        
        # Test actual provider call
        print("TESTING PROVIDER CALL:")
        print("-" * 40)
        
        test_payload = {
            "messages": [{"role": "user", "content": "Hello, test message"}]
        }
        
        try:
            result = orchestrator.generate(test_payload, timeout=10)
            print(f"Result: {result}")
            
            if result.get("success"):
                print("✅ PROVIDER CALL SUCCEEDED")
            else:
                print(f"❌ PROVIDER CALL FAILED: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ PROVIDER CALL EXCEPTION: {e}")
        
    except Exception as e:
        print(f"❌ ERROR loading orchestrator: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()