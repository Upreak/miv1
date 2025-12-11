#!/usr/bin/env python3
"""
Comprehensive API Key Validation Script
Tests each provider API key individually to identify valid/invalid keys
"""

import os
import sys
import json
from pathlib import Path

# Add the Backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

def load_env_file():
    """Load environment variables from .env file"""
    env_vars = {}
    env_file = Path(".env")
    
    if not env_file.exists():
        print(f"[ERROR] .env file not found at {env_file.absolute()}")
        return env_vars
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def test_openrouter_api(provider_key, provider_model, provider_baseurl):
    """Test OpenRouter API key"""
    print(f"\n🔍 Testing OpenRouter API Key...")
    print(f"   Model: {provider_model}")
    print(f"   Base URL: {provider_baseurl}")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=provider_key,
            base_url=provider_baseurl
        )
        
        # Test with a simple request
        response = client.chat.completions.create(
            model=provider_model,
            messages=[{"role": "user", "content": "Hello! Just respond with 'OK' to test the connection."}],
            max_tokens=10,
            timeout=30
        )
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            print(f"   ✅ SUCCESS: API key is valid")
            print(f"   📝 Response: {content}")
            return True, "Valid API key"
        else:
            print(f"   ❌ FAILED: No response received")
            return False, "No response received"
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ FAILED: {error_msg}")
        
        # Categorize the error
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            return False, "Invalid API key (401 Unauthorized)"
        elif "403" in error_msg:
            return False, "Forbidden - API key may be restricted (403)"
        elif "404" in error_msg:
            return False, "Not found - Invalid model or endpoint (404)"
        elif "rate limit" in error_msg.lower():
            return False, "Rate limited"
        else:
            return False, f"Authentication error: {error_msg}"

def test_gemini_api(provider_key, provider_model):
    """Test Gemini API key"""
    print(f"\n🔍 Testing Gemini API Key...")
    print(f"   Model: {provider_model}")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=provider_key)
        model = genai.GenerativeModel(provider_model)
        
        # Test with a simple request
        response = model.generate_content("Hello! Just respond with 'OK' to test the connection.")
        
        if response.text:
            print(f"   ✅ SUCCESS: API key is valid")
            print(f"   📝 Response: {response.text}")
            return True, "Valid API key"
        else:
            print(f"   ❌ FAILED: No response received")
            return False, "No response received"
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ FAILED: {error_msg}")
        
        # Categorize the error
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            return False, "Invalid API key (401 Unauthorized)"
        elif "403" in error_msg:
            return False, "Forbidden - API key may be leaked/restricted (403)"
        elif "API_KEY_INVALID" in error_msg:
            return False, "Invalid API key format"
        elif "rate limit" in error_msg.lower():
            return False, "Rate limited"
        else:
            return False, f"Authentication error: {error_msg}"

def test_groq_api(provider_key, provider_model):
    """Test Groq API key"""
    print(f"\n🔍 Testing Groq API Key...")
    print(f"   Model: {provider_model}")
    
    try:
        from groq import Groq
        
        client = Groq(api_key=provider_key)
        
        # Test with a simple request
        response = client.chat.completions.create(
            model=provider_model,
            messages=[{"role": "user", "content": "Hello! Just respond with 'OK' to test the connection."}],
            max_tokens=10,
            temperature=0.1
        )
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            print(f"   [SUCCESS] API key is valid")
            print(f"   [RESPONSE] {content}")
            return True, "Valid API key"
        else:
            print(f"   [FAILED] No response received")
            return False, "No response received"
            
    except Exception as e:
        error_msg = str(e)
        print(f"   [FAILED] {error_msg}")
        
        # Categorize the error
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            return False, "Invalid API key (401 Unauthorized)"
        elif "403" in error_msg:
            return False, "Forbidden - API key may be restricted (403)"
        elif "invalid_api_key" in error_msg.lower():
            return False, "Invalid API key"
        elif "rate limit" in error_msg.lower():
            return False, "Rate limited"
        else:
            return False, f"Authentication error: {error_msg}"

def main():
    print("=" * 80)
    print("COMPREHENSIVE API KEY VALIDATION")
    print("=" * 80)
    
    # Load environment variables
    env_vars = load_env_file()
    if not env_vars:
        print("[ERROR] Failed to load environment variables")
        return
    
    print(f"[INFO] Loaded .env file with {len(env_vars)} variables")
    
    # Test results
    results = {}
    
    # Test Provider 1 - OpenRouter
    print("\n" + "=" * 60)
    print("TESTING PROVIDER 1 - OpenRouter")
    print("=" * 60)
    
    provider1_key = env_vars.get("PROVIDER1_KEY")
    provider1_model = env_vars.get("PROVIDER1_MODEL", "x-ai/grok-4.1-fast:free")
    provider1_baseurl = env_vars.get("PROVIDER1_BASEURL", "https://openrouter.ai/api/v1")
    
    if provider1_key:
        success, message = test_openrouter_api(provider1_key, provider1_model, provider1_baseurl)
        results["provider1_openrouter"] = {
            "key": provider1_key[:20] + "..." if len(provider1_key) > 20 else provider1_key,
            "model": provider1_model,
            "success": success,
            "message": message
        }
    else:
        results["provider1_openrouter"] = {
            "key": "NOT FOUND",
            "model": provider1_model,
            "success": False,
            "message": "API key not found in .env file"
        }
    
    # Test Provider 2 - Gemini
    print("\n" + "=" * 60)
    print("TESTING PROVIDER 2 - Gemini")
    print("=" * 60)
    
    provider2_key = env_vars.get("PROVIDER2_KEY")
    provider2_model = env_vars.get("PROVIDER2_MODEL", "gemini-2.5-flash-lite")
    
    if provider2_key:
        success, message = test_gemini_api(provider2_key, provider2_model)
        results["provider2_gemini"] = {
            "key": provider2_key[:20] + "..." if len(provider2_key) > 20 else provider2_key,
            "model": provider2_model,
            "success": success,
            "message": message
        }
    else:
        results["provider2_gemini"] = {
            "key": "NOT FOUND",
            "model": provider2_model,
            "success": False,
            "message": "API key not found in .env file"
        }
    
    # Test Provider 3 - Groq
    print("\n" + "=" * 60)
    print("TESTING PROVIDER 3 - Groq")
    print("=" * 60)
    
    provider3_key = env_vars.get("PROVIDER3_KEY")
    provider3_model = env_vars.get("PROVIDER3_MODEL", "openai/gpt-oss-120b")
    
    if provider3_key:
        success, message = test_groq_api(provider3_key, provider3_model)
        results["provider3_groq"] = {
            "key": provider3_key[:20] + "..." if len(provider3_key) > 20 else provider3_key,
            "model": provider3_model,
            "success": success,
            "message": message
        }
    else:
        results["provider3_groq"] = {
            "key": "NOT FOUND",
            "model": provider3_model,
            "success": False,
            "message": "API key not found in .env file"
        }
    
    # Test Provider 4 - OpenRouter
    print("\n" + "=" * 60)
    print("TESTING PROVIDER 4 - OpenRouter")
    print("=" * 60)
    
    provider4_key = env_vars.get("PROVIDER4_KEY")
    provider4_model = env_vars.get("PROVIDER4_MODEL", "z-ai/glm-4.5-air:free")
    provider4_baseurl = env_vars.get("PROVIDER4_BASEURL", "https://openrouter.ai/api/v1")
    
    if provider4_key:
        success, message = test_openrouter_api(provider4_key, provider4_model, provider4_baseurl)
        results["provider4_openrouter"] = {
            "key": provider4_key[:20] + "..." if len(provider4_key) > 20 else provider4_key,
            "model": provider4_model,
            "success": success,
            "message": message
        }
    else:
        results["provider4_openrouter"] = {
            "key": "NOT FOUND",
            "model": provider4_model,
            "success": False,
            "message": "API key not found in .env file"
        }
    
    # Summary
    print("\n" + "=" * 80)
    print("API KEY VALIDATION SUMMARY")
    print("=" * 80)
    
    successful_providers = []
    failed_providers = []
    
    for provider_id, result in results.items():
        status = "✅ WORKING" if result["success"] else "❌ FAILED"
        print(f"\n{provider_id.upper()}:")
        print(f"   Status: {status}")
        print(f"   Model: {result['model']}")
        print(f"   Key: {result['key']}")
        print(f"   Message: {result['message']}")
        
        if result["success"]:
            successful_providers.append(provider_id)
        else:
            failed_providers.append(provider_id)
    
    print(f"\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    print(f"✅ Working Providers: {len(successful_providers)}")
    for provider in successful_providers:
        print(f"   - {provider}")
    
    print(f"\n❌ Failed Providers: {len(failed_providers)}")
    for provider in failed_providers:
        print(f"   - {provider}")
    
    if successful_providers:
        print(f"\n🎉 SUCCESS: {len(successful_providers)} provider(s) are working!")
        print("The Brain Module should function with these providers.")
    else:
        print(f"\n💥 FAILURE: No working API keys found!")
        print("Please update your .env file with valid API keys.")
    
    # Save results to file
    results_file = Path("api_key_validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")

if __name__ == "__main__":
    main()