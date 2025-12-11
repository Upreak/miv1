#!/usr/bin/env python3
"""
Simple test to verify Brain Module is working by sending "hi" to chat mode
"""

import sys
import os
import requests
import json
import time
from threading import Thread

# Add the backend_app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_app'))

def start_server():
    """Start the FastAPI server in background"""
    os.chdir('backend_app')
    os.system('python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &')

def test_brain_chat():
    """Test brain module with simple chat"""
    print("🧪 Testing Brain Module with 'hi' message...")
    
    # Wait for server to start
    time.sleep(3)
    
    url = "http://localhost:8000/api/v1/brain/process"
    
    request_data = {
        "mode": "chat",
        "text": "hi",
        "metadata": {
            "session_id": "test_session_123"
        }
    }
    
    try:
        print(f"📤 Sending request to: {url}")
        print(f"📝 Request data: {json.dumps(request_data, indent=2)}")
        
        response = requests.post(url, json=request_data, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Brain Module is working!")
            print("\n📤 Response:")
            print(json.dumps(result, indent=2))
            
            # Show key fields
            print(f"\n🔍 Key Response Fields:")
            print(f"  - Success: {result.get('success')}")
            print(f"  - Mode: {result.get('mode')}")
            print(f"  - Intent: {result.get('intent')}")
            print(f"  - Provider: {result.get('provider')}")
            print(f"  - Data: {result.get('data')}")
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("Make sure the server is running on port 8000")

if __name__ == "__main__":
    print("🚀 Starting Brain Module Chat Test")
    print("=" * 50)
    
    # Start server in background
    print("Starting FastAPI server...")
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Run test
    test_brain_chat()