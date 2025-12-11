#!/usr/bin/env python3
"""
Test script to directly test the Brain Module Provider Orchestrator
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add the Backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from backend_app.brain_module.providers.provider_orchestrator import ProviderOrchestrator
from backend_app.brain_module.utils.logger import get_logger

logger = get_logger("brain_orchestrator_test")

async def test_brain_orchestrator():
    """Test the Brain Module Provider Orchestrator directly"""
    
    print("=" * 70)
    print("Testing Brain Module Provider Orchestrator")
    print("=" * 70)
    
    # Test time
    test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Test time: {test_time}")
    
    # Check environment variables
    print(f"\n[INFO] Environment variables loaded from .env")
    
    # Create provider orchestrator
    print(f"\n[INFO] Initializing Provider Orchestrator...")
    try:
        orchestrator = ProviderOrchestrator()
        print(f"[SUCCESS] Provider Orchestrator initialized")
        print(f"[INFO] Found {len(orchestrator.providers)} providers")
        
        # List configured providers
        for i, provider in enumerate(orchestrator.providers):
            print(f"[INFO] Provider {i+1}: {provider['type']} (slot {provider['slot']}, model: {provider['model']})")
            
    except Exception as e:
        print(f"[ERROR] Failed to initialize Provider Orchestrator: {e}")
        return
    
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
    
    print(f"\n{'='*70}")
    print("Testing Provider Orchestrator")
    print(f"{'='*70}")
    
    try:
        print(f"[INFO] Testing Provider Orchestrator with simple request...")
        
        # Make the API call (provider orchestrator.generate is synchronous)
        result = orchestrator.generate(test_payload)
        
        print(f"\n[RESULT] Provider Orchestrator Response:")
        print(f"[RESULT] Success: {result.get('success', False)}")
        print(f"[RESULT] Provider: {result.get('provider', 'None')}")
        print(f"[RESULT] Model: {result.get('model', 'None')}")
        print(f"[RESULT] Response: {result.get('response', 'No response')[:100]}...")
        print(f"[RESULT] Usage: {result.get('usage', {})}")
        print(f"[RESULT] Error: {result.get('error', 'None')}")
        
        if result.get("success"):
            print(f"\n[SUCCESS] Provider Orchestrator is working!")
            return True
        else:
            error = result.get('error', 'Unknown error')
            print(f"\n[FAILED] Provider Orchestrator failed: {error}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Exception testing Provider Orchestrator: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_brain_orchestrator())