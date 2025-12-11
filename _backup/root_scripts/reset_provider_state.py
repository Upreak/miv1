#!/usr/bin/env python3
"""
Reset provider usage state to clear cooldowns
"""

import json
from pathlib import Path

state_file = Path("Backend/backend_app/brain_module/providers/provider_usage_state.json")

if state_file.exists():
    # Create backup
    backup_file = Path("Backend/backend_app/brain_module/providers/provider_usage_state_backup.json")
    with open(state_file, 'r') as f:
        backup_data = f.read()
    with open(backup_file, 'w') as f:
        f.write(backup_data)
    
    # Reset state
    reset_state = {}
    with open(state_file, 'w') as f:
        json.dump(reset_state, f, indent=2)
    
    print(f"Provider usage state reset successfully!")
    print(f"Backup saved to: {backup_file}")
else:
    print("Provider usage state file not found")