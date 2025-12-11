#!/usr/bin/env python3
"""
Debug script to test provider factory directly
"""

import os
import sys
sys.path.append('Backend/backend_app')

from brain_module.providers.provider_factory import create_provider_from_env

print("=" * 60)
print("DEBUG: Provider Factory Test")
print("=" * 60)

# Check environment variables
print("ENVIRONMENT VARIABLES:")
for i in range(1, 6):
    type_var = f"PROVIDER{i}_TYPE"
    key_var = f"PROVIDER{i}_KEY"
    model_var = f"PROVIDER{i}_MODEL"
    
    provider_type = os.getenv(type_var, "NOT_SET")
    provider_key = os.getenv(key_var, "NOT_SET")
    provider_model = os.getenv(model_var, "NOT_SET")
    
    print(f"Provider {i}:")
    print(f"  Type: {provider_type}")
    print(f"  Key: {'*' * 20 if provider_key != 'NOT_SET' else 'NOT_SET'}")
    print(f"  Model: {provider_model}")
    print()

print("PROVIDER CREATION TEST:")
print("-" * 40)

for i in range(1, 6):
    try:
        provider = create_provider_from_env(i)
        if provider:
            print(f"SUCCESS: Provider {i} created - {provider.name} ({provider.model})")
        else:
            print(f"FAILED: Provider {i} - No provider created")
    except Exception as e:
        print(f"ERROR: Provider {i} - {str(e)}")