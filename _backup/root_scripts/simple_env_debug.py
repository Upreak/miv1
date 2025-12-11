#!/usr/bin/env python3
"""
Simple debug script to check environment variable loading
"""

import os
from dotenv import load_dotenv

print("=== ENVIRONMENT VARIABLE DEBUG ===")
print()

# Check if .env file exists
env_path = '.env'
if os.path.exists(env_path):
    print(f"SUCCESS: .env file found at: {os.path.abspath(env_path)}")
    
    # Load environment variables
    load_dotenv(env_path)
    print("SUCCESS: Environment variables loaded")
else:
    print(f"ERROR: .env file NOT found at: {os.path.abspath(env_path)}")
    print("ERROR: Checking other possible locations...")
    
    # Check other possible locations
    possible_paths = [
        'Backend/.env',
        './Backend/.env',
        '../.env',
        '../../.env'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"SUCCESS: Found .env at: {os.path.abspath(path)}")
            load_dotenv(path)
            break
    else:
        print("ERROR: No .env file found in any of the checked locations")
        exit(1)

print()
print("=== PROVIDER ENVIRONMENT VARIABLES ===")

# Check provider variables
provider_vars = []
for i in range(1, 6):  # Check slots 1-5
    key_var = f'PROVIDER{i}_KEY'
    type_var = f'PROVIDER{i}_TYPE'
    
    if key_var in os.environ:
        key = os.environ[key_var]
        masked_key = key[:8] + "*" * (len(key) - 12) + key[-4:] if len(key) > 12 else "*" * len(key)
        provider_type = os.environ.get(type_var, 'UNKNOWN')
        provider_vars.append(i)
        print(f"SUCCESS: Provider {i}: {provider_type} - {masked_key}")
    else:
        print(f"ERROR: Provider {i}: {key_var} NOT FOUND")

print()
print(f"Total providers configured: {len(provider_vars)}")

if len(provider_vars) == 0:
    print("ERROR: NO PROVIDERS CONFIGURED - This explains 'All providers failed'")
    print()
    print("=== SOLUTION ===")
    print("1. Ensure .env file is in the correct location")
    print("2. Ensure PROVIDER*_KEY variables are set in .env file")
    print("3. Restart the application after making changes")
else:
    print("SUCCESS: Providers are configured correctly")
    
    # Test provider creation
    print()
    print("=== PROVIDER CREATION TEST ===")
    
    try:
        import sys
        sys.path.append('Backend/backend_app')
        from brain_module.providers.provider_factory import create_provider_from_env
        
        for slot in provider_vars:
            try:
                provider = create_provider_from_env(slot)
                if provider:
                    print(f"SUCCESS: Provider {slot}: {provider.name} ({provider.model})")
                else:
                    print(f"ERROR: Provider {slot}: No provider created")
            except Exception as e:
                print(f"ERROR: Provider {slot}: {str(e)}")
                
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")