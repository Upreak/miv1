#!/usr/bin/env python3
"""
Debug script to analyze provider status and identify root cause
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

logger = get_logger("debug")

def analyze_provider_status():
    """Analyze current provider status and identify issues"""
    
    print("=" * 60)
    print("🔍 PROVIDER STATUS ANALYSIS")
    print("=" * 60)
    
    # Check current time
    current_timestamp = int(time.time())
    current_time = datetime.fromtimestamp(current_timestamp)
    print(f"📅 Current Time: {current_time} (timestamp: {current_timestamp})")
    print()
    
    # Load provider orchestrator
    try:
        orchestrator = ProviderOrchestrator()
        print(f"✅ Provider Orchestrator loaded successfully")
        print(f"📊 Total providers configured: {len(orchestrator.providers)}")
        print()
        
        # Check each provider
        for provider in orchestrator.providers:
            slot = provider["slot"]
            provider_id = f"provider{slot}_{provider['type']}"
            provider_name = provider["type"]
            model = provider["model"]
            
            print(f"🔧 Provider {slot} ({provider_name}):")
            print(f"   Model: {model}")
            print(f"   ID: {provider_id}")
            
            # Check usage status
            usage_status = orchestrator.usage.get_usage_state(provider_id)
            if usage_status:
                cooldown_until = usage_status.get("cooldown_until", 0)
                count = usage_status.get("count", 0)
                
                if cooldown_until > current_timestamp:
                    cooldown_remaining = cooldown_until - current_timestamp
                    cooldown_hours = cooldown_remaining // 3600
                    cooldown_minutes = (cooldown_remaining % 3600) // 60
                    print(f"   ❌ Status: COOLDOWN (expires in {cooldown_hours}h {cooldown_minutes}m)")
                    print(f"   📊 Usage count: {count}")
                else:
                    print(f"   ✅ Status: AVAILABLE")
                    print(f"   📊 Usage count: {count}")
            else:
                print(f"   ❓ Status: NO USAGE DATA")
            
            print()
        
        # Test API key validation
        print("🔑 API Key Validation:")
        for i in range(1, 5):
            key_var = f"PROVIDER{i}_KEY"
            if key_var in os.environ:
                key = os.environ[key_var]
                masked_key = key[:8] + "*" * (len(key) - 12) + key[-4:]
                print(f"   Provider {i}: {masked_key}")
            else:
                print(f"   Provider {i}: ❌ NO ENV VAR")
        print()
        
        # Test provider creation
        print("🏗️  Provider Creation Test:")
        for i in range(1, 5):
            try:
                from brain_module.providers.provider_factory import create_provider_from_env
                provider = create_provider_from_env(i)
                if provider:
                    print(f"   Provider {i}: ✅ SUCCESS ({provider.name})")
                else:
                    print(f"   Provider {i}: ❌ FAILED (no provider created)")
            except Exception as e:
                print(f"   Provider {i}: ❌ ERROR ({str(e)[:50]}...)")
        print()
        
        # Check usage state file
        print("📁 Usage State File:")
        usage_file = "Backend/backend_app/brain_module/providers/provider_usage_state.json"
        if os.path.exists(usage_file):
            with open(usage_file, 'r') as f:
                usage_data = json.load(f)
                print(f"   File exists with {len(usage_data)} providers")
                for provider_id, state in usage_data.items():
                    cooldown_until = state.get("cooldown_until", 0)
                    if cooldown_until > current_timestamp:
                        remaining = cooldown_until - current_timestamp
                        print(f"   {provider_id}: COOLDOWN ({remaining}s remaining)")
                    else:
                        print(f"   {provider_id}: AVAILABLE")
        else:
            print(f"   ❌ File not found")
        
    except Exception as e:
        print(f"❌ ERROR loading orchestrator: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_provider_status()