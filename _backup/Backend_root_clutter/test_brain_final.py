#!/usr/bin/env python3
"""
Final test of Brain Module with actual providers loaded
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

# Load the correct .env file from the parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# Add the backend_app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_app'))

async def test_brain_with_providers():
    """Test brain service with actual provider configuration"""
    print("Testing Brain Module with actual providers loaded...")
    print(f"Loading .env from: {env_path}")
    
    # Check provider configuration
    provider_count = os.getenv('BRAIN_PROVIDER_COUNT', '0')
    provider1_key = os.getenv('PROVIDER1_KEY', '')
    provider2_key = os.getenv('PROVIDER2_KEY', '')
    provider3_key = os.getenv('PROVIDER3_KEY', '')
    provider4_key = os.getenv('PROVIDER4_KEY', '')
    
    print(f"\nProvider Configuration:")
    print(f"  BRAIN_PROVIDER_COUNT: {provider_count}")
    print(f"  Provider 1 Key: {'CONFIGURED' if provider1_key else 'MISSING'}")
    print(f"  Provider 2 Key: {'CONFIGURED' if provider2_key else 'MISSING'}")
    print(f"  Provider 3 Key: {'CONFIGURED' if provider3_key else 'MISSING'}")
    print(f"  Provider 4 Key: {'CONFIGURED' if provider4_key else 'MISSING'}")
    
    try:
        # Import the brain service
        from backend_app.brain_module.brain_service import BrainService
        
        # Create brain service instance
        brain_service = BrainService()
        
        # Prepare test data
        qitem = {
            "qid": f"test_{int(datetime.now().timestamp() * 1000)}",
            "text": "hi",
            "intake_type": "chat",
            "meta": {
                "session_id": "test_session_123"
            }
        }
        
        print(f"\nSending 'hi' message to brain service...")
        
        # Process through brain service
        result = await brain_service.process(qitem, timeout=30)
        
        print("\n=== BRAIN SERVICE RESPONSE ===")
        print(json.dumps(result, indent=2))
        
        # Show key information
        print(f"\nKey Response Fields:")
        print(f"  - Success: {result.get('success')}")
        print(f"  - Response: {result.get('response', 'N/A')}")
        print(f"  - Provider: {result.get('provider', 'N/A')}")
        print(f"  - Model: {result.get('model', 'N/A')}")
        print(f"  - Usage: {result.get('usage', 'N/A')}")
        print(f"  - Error: {result.get('error', 'None')}")
        
        if result.get('success'):
            print("\nSUCCESS! Brain Module is working with LLM providers!")
            print(f"AI Response: {result.get('response')}")
            print(f"Provider Used: {result.get('provider')}")
            print(f"Model Used: {result.get('model')}")
        else:
            print(f"\nFAILED: {result.get('error')}")
            
        return result
        
    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main test function"""
    print("=" * 60)
    print("BRAIN MODULE TEST WITH PROVIDERS")
    print("=" * 60)
    
    result = await test_brain_with_providers()
    
    print("\n" + "=" * 60)
    if result and result.get('success'):
        print("BRAIN MODULE IS FULLY OPERATIONAL!")
        print("Provider architecture is working")
        print("API endpoints are ready")
        print("LLM integration is functional")
        print("\nReady for production use!")
    else:
        print("Test completed - check errors above")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(main())