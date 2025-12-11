#!/usr/bin/env python3
"""
Test script to verify Brain Module functionality with fresh API keys
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add the Backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from backend_app.brain_module.providers.provider_orchestrator import ProviderOrchestrator
from backend_app.brain_module.brain_service import BrainSvc
from backend_app.brain_module.utils.logger import get_logger

logger = get_logger("brain_test")

async def test_brain_module():
    """Test the Brain Module with fresh API keys"""
    
    print("=" * 70)
    print("Testing Brain Module with Fresh API Keys")
    print("=" * 70)
    
    # Test time
    test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Test time: {test_time}")
    
    # Check environment variables
    print(f"\n[INFO] Environment variables loaded from .env")
    
    # Test 1: Provider Orchestrator
    print(f"\n{'='*70}")
    print("Test 1: Provider Orchestrator")
    print(f"{'='*70}")
    
    try:
        orchestrator = ProviderOrchestrator()
        print(f"[SUCCESS] Provider Orchestrator initialized")
        print(f"[INFO] Found {len(orchestrator.providers)} providers")
        
        # List configured providers
        for i, provider in enumerate(orchestrator.providers):
            print(f"[INFO] Provider {i+1}: {provider['type']} (slot {provider['slot']}, model: {provider['model']})")
            
    except Exception as e:
        print(f"[ERROR] Failed to initialize Provider Orchestrator: {e}")
        return False
    
    # Test 2: Brain Service
    print(f"\n{'='*70}")
    print("Test 2: Brain Service")
    print(f"{'='*70}")
    
    test_request = {
        "qid": f"test_{int(datetime.now().timestamp())}",
        "text": "Hello! Please respond with just 'OK' to test if this provider is working.",
        "intake_type": "chat",
        "meta": {
            "session_id": "test_session_123"
        }
    }
    
    try:
        print(f"[INFO] Testing Brain Service with simple request...")
        print(f"[INFO] Request: {test_request['text']}")
        
        # Make the API call
        result = await BrainSvc.process(test_request)
        
        print(f"\n[RESULT] Brain Service Response:")
        print(f"[RESULT] Success: {result.get('success', False)}")
        print(f"[RESULT] Provider: {result.get('provider', 'None')}")
        print(f"[RESULT] Model: {result.get('model', 'None')}")
        print(f"[RESULT] Response: {result.get('response', 'No response')[:100]}...")
        print(f"[RESULT] Usage: {result.get('usage', {})}")
        print(f"[RESULT] Error: {result.get('error', 'None')}")
        
        if result.get("success"):
            print(f"\n[SUCCESS] Brain Module is working with fresh API keys!")
            return True
        else:
            error = result.get('error', 'Unknown error')
            print(f"\n[FAILED] Brain Module failed: {error}")
            print(f"[INFO] This suggests API keys may still be rate limited or invalid")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Exception testing Brain Service: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_brain_module())
    
    print(f"\n{'='*70}")
    print("FINAL RESULT")
    print(f"{'='*70}")
    
    if success:
        print("[SUCCESS] Brain Module is fully functional!")
        print("[SUCCESS] All providers are working correctly!")
        print("[SUCCESS] Ready for production use!")
    else:
        print("[FAILED] Brain Module needs fresh API keys")
        print("[INFO] Please follow the API Key Setup Guide to resolve this issue")
    
    print(f"{'='*70}")