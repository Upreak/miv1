#!/usr/bin/env python3
"""
Diagnostic script to analyze the cooldown issue in Brain Module
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add the Backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

def analyze_cooldown_state():
    """Analyze the current cooldown state and identify issues"""
    
    print("=" * 80)
    print("BRAIN MODULE COOLDOWN ANALYSIS")
    print("=" * 80)
    
    # Current timestamp
    current_ts = int(datetime.now().timestamp())
    current_time = datetime.fromtimestamp(current_ts)
    
    print(f"Current Time: {current_time} (UTC)")
    print(f"Current Timestamp: {current_ts}")
    print()
    
    # Read the provider usage state
    state_file = Path("Backend/backend_app/brain_module/providers/provider_usage_state.json")
    
    if not state_file.exists():
        print("[ERROR] Provider usage state file not found!")
        return
    
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read state file: {e}")
        return
    
    print("PROVIDER COOLDOWN ANALYSIS:")
    print("-" * 50)
    
    issues_found = []
    
    for provider_id, provider_data in state.items():
        print(f"\nProvider: {provider_id}")
        print(f"  Date: {provider_data.get('date', 'N/A')}")
        print(f"  Count: {provider_data.get('count', 0)}")
        
        cooldown_until = provider_data.get('cooldown_until', 0)
        cooldown_time = datetime.fromtimestamp(cooldown_until)
        
        print(f"  Cooldown Until: {cooldown_time} (UTC)")
        print(f"  Cooldown Timestamp: {cooldown_until}")
        
        # Calculate time remaining
        if cooldown_until > current_ts:
            time_remaining = cooldown_until - current_ts
            hours_remaining = time_remaining // 3600
            minutes_remaining = (time_remaining % 3600) // 60
            
            print(f"  Time Remaining: {hours_remaining}h {minutes_remaining}m")
            
            # Check if cooldown is excessive
            if time_remaining > 24 * 3600:  # More than 24 hours
                print(f"  [ISSUE] Excessive cooldown period detected!")
                issues_found.append({
                    "provider": provider_id,
                    "issue": "excessive_cooldown",
                    "remaining_hours": time_remaining / 3600
                })
            
            # Check if cooldown was set recently but shouldn't be
            elif time_remaining > 3600 and provider_data.get('count', 0) == 0:
                print(f"  [ISSUE] Provider on cooldown but no successful requests made!")
                issues_found.append({
                    "provider": provider_id,
                    "issue": "cooldown_without_usage",
                    "count": provider_data.get('count', 0)
                })
        else:
            print(f"  [OK] Cooldown expired")
    
    print("\n" + "=" * 80)
    print("ISSUE SUMMARY")
    print("=" * 80)
    
    if issues_found:
        print(f"Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"\n{i}. Provider: {issue['provider']}")
            print(f"   Issue: {issue['issue']}")
            if issue['issue'] == 'excessive_cooldown':
                print(f"   Remaining cooldown: {issue['remaining_hours']:.1f} hours")
            elif issue['issue'] == 'cooldown_without_usage':
                print(f"   Request count: {issue['count']}")
    else:
        print("No issues found in cooldown state")
    
    print("\n" + "=" * 80)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 80)
    
    # Analyze the root cause
    print("Possible root causes:")
    print("1. Wrong .env file was used previously, setting cooldowns on invalid API keys")
    print("2. Cooldown logic is too aggressive (24 hours by default)")
    print("3. No automatic cooldown reset when switching .env files")
    print("4. Provider failures are being treated as rate limits")
    
    print("\n" + "=" * 80)
    print("RECOMMENDED SOLUTIONS")
    print("=" * 80)
    
    print("1. Reset the provider usage state file")
    print("2. Modify cooldown logic to be more reasonable")
    print("3. Add automatic cooldown reset when environment changes")
    print("4. Differentiate between API failures and rate limits")
    
    # Check if we should reset the state
    print("\n" + "=" * 80)
    print("AUTOMATIC RECOMMENDATION")
    print("=" * 80)
    
    if any(issue['issue'] == 'excessive_cooldown' for issue in issues_found):
        print("RECOMMENDATION: Reset provider usage state file")
        print("This will clear all cooldown periods and allow fresh starts")
        
        # Create a reset script
        reset_script = '''#!/usr/bin/env python3
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
'''
        
        with open("reset_provider_state.py", 'w') as f:
            f.write(reset_script)
        
        print(f"✅ Created reset script: reset_provider_state.py")
        print(f"   Run this script to clear all cooldowns")

if __name__ == "__main__":
    analyze_cooldown_state()