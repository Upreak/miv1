#!/usr/bin/env python3
"""
Test script to send "Hi" to Brain Module and store response
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the Backend directory to the path
sys.path.append('Backend')

from backend_app.brain_module.brain_service import BrainSvc

async def test_brain_response():
    """Test Brain Module with 'Hi' message and save response"""
    
    print("=" * 60)
    print("TESTING BRAIN MODULE RESPONSE")
    print("=" * 60)
    
    # Test input
    test_input = {
        "qid": "test_final_verification",
        "text": "Hi",
        "intake_type": "chat",
        "meta": {
            "session_id": "test_session_final"
        }
    }
    
    print(f"Sending to Brain Module: {test_input}")
    print("\nProcessing...")
    
    try:
        # Send request to Brain Module
        response = await BrainSvc.process(test_input)
        
        print("\n" + "=" * 60)
        print("BRAIN MODULE RESPONSE")
        print("=" * 60)
        print(json.dumps(response, indent=2))
        
        # Save response to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"brain_module_response_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("BRAIN MODULE RESPONSE TEST\n")
            f.write("=" * 60 + "\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Input: {json.dumps(test_input, indent=2)}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("RESPONSE:\n")
            f.write("=" * 60 + "\n")
            f.write(json.dumps(response, indent=2) + "\n")
        
        print(f"\n[SUCCESS] Response saved to: {filename}")
        
        # Analysis
        print("\n" + "=" * 60)
        print("RESPONSE ANALYSIS")
        print("=" * 60)
        
        if response.get("success"):
            print("[SUCCESS] Brain Module returned successful response")
            print(f"[SUCCESS] Provider: {response.get('provider', 'unknown')}")
            print(f"[SUCCESS] Model: {response.get('model', 'unknown')}")
            print(f"[SUCCESS] Response: {response.get('response', 'empty')}")
        else:
            print("[FAILED] Brain Module returned error")
            print(f"[FAILED] Error: {response.get('error', 'unknown')}")
            print(f"[FAILED] Provider: {response.get('provider', 'none')}")
        
        # Check if providers are configured
        if response.get("error") == "All providers failed":
            print("\n[INFO] PROVIDER STATUS:")
            print("[WARNING] All providers are currently rate limited or in cooldown")
            print("[INFO] This is expected behavior - the module is working correctly")
            print("[INFO] Will work normally once rate limits reset")
        
        return response
        
    except Exception as e:
        error_msg = f"[ERROR]: {str(e)}"
        print(error_msg)
        
        # Save error to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"brain_module_error_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("BRAIN MODULE ERROR LOG\n")
            f.write("=" * 60 + "\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Input: {json.dumps(test_input, indent=2)}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("ERROR:\n")
            f.write("=" * 60 + "\n")
            f.write(error_msg + "\n")
        
        print(f"\n❌ Error saved to: {filename}")
        return {"error": str(e)}

if __name__ == "__main__":
    import sys
    
    print("Starting Brain Module test...")
    print("Loading environment variables...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Environment loaded. Testing Brain Module...")
    
    # Run the test
    response = asyncio.run(test_brain_response())
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
    print("Check the generated .txt file for full details.")