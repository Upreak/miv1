#!/usr/bin/env python3
"""
Debug script to check environment variable loading
"""

import os
import sys
from dotenv import load_dotenv

print("=" * 60)
print("DEBUG: Environment Variable Loading")
print("=" * 60)

# Check if .env file exists
env_path = '.env'
print(f"Looking for .env file at: {os.path.abspath(env_path)}")
print(f"File exists: {os.path.exists(env_path)}")

# Load environment variables
print("\nLoading environment variables...")
load_dotenv(env_path)
print("Environment variables loaded")

# Check specific provider variables
print("\nPROVIDER ENVIRONMENT VARIABLES:")
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

# Check all environment variables
print("\nALL ENVIRONMENT VARIABLES:")
env_vars = {k: v for k, v in os.environ.items() if 'PROVIDER' in k}
for key, value in env_vars.items():
    print(f"{key}: {'*' * 20 if 'KEY' in key else value}")