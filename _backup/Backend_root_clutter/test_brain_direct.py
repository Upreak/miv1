#!/usr/bin/env python3
"""
Direct test of Brain Module service with "hi" message
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the backend_app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_app'))

async def test_brain_service():
    """Test brain service directly"""
    print("Testing Brain Module with 'hi' message...")
    
    try:
        # Import the brain service
        from backend_app.brain_module.brain_service import BrainService
        
        # Create brain service instance
        brain_service = BrainService()
        
        # Prepare test data - using the QItem format that the service expects
        qitem = {
            "qid": f"test_{int(datetime.now().timestamp() * 1000)}",
            "text": "hi",
            "intake_type": "chat",
            "meta": {
                "session_id": "test_session_123"
            }
        }
        
        print(f"Test data: {json.dumps(qitem, indent=2)}")
        print("Sending to brain service...")
        
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
            print("\nSUCCESS! Brain Module is working!")
            print(f"AI Response: {result.get('response')}")
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
    print("=== BRAIN MODULE DIRECT TEST ===")
    print("Testing brain service directly without HTTP server")
    print()
    
    result = await test_brain_service()
    
    print("\n" + "="*50)
    if result and result.get('success'):
        print("BRAIN MODULE IS OPERATIONAL!")
        print("Ready for production use")
    else:
        print("Test completed - check errors above")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(main())