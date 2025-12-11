#!/usr/bin/env python3
"""
Complete Telegram Bot Setup and Run Script with Cloudflare Tunnel
This script will set up and run your Telegram bot using Cloudflare Tunnel
"""

import os
import sys
import subprocess
import time
import secrets
import re
import threading
import signal

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a step with description"""
    print(f"\n{step}️⃣  {description}")
    print("-" * 40)

def generate_webhook_secret():
    """Generate a secure webhook secret"""
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))

def update_env_file(bot_token, webhook_secret, webhook_url):
    """Update the .env file with all necessary values"""
    print_step("📝", "Updating .env file...")
    
    # Read current .env file or create if not exists
    content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
    
    # Dictionary of keys to update
    updates = {
        'TELEGRAM_BOT_TOKEN': bot_token,
        'TELEGRAM_WEBHOOK_SECRET': webhook_secret,
        'TELEGRAM_WEBHOOK_URL': webhook_url
    }
    
    # Update regular lines
    lines = content.splitlines()
    new_lines = []
    keys_found = set()
    
    for line in lines:
        line_key = line.split('=')[0].strip() if '=' in line else None
        if line_key in updates:
            new_lines.append(f"{line_key}={updates[line_key]}")
            keys_found.add(line_key)
        else:
            new_lines.append(line)
            
    # Add missing keys
    for key, value in updates.items():
        if key not in keys_found:
            new_lines.append(f"{key}={value}")
            
    # Write back
    with open('.env', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ Bot token updated")
    print(f"✅ Webhook secret updated")
    print(f"✅ Webhook URL: {webhook_url}")

def check_cloudflared():
    """Check if cloudflared is installed, download if not"""
    print_step("☁️", "Checking Cloudflare Tunnel...")
    
    if os.path.exists("cloudflared.exe"):
        print("✅ cloudflared.exe found")
        return True
        
    print("⏳ cloudflared.exe not found. Downloading...")
    try:
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        import urllib.request
        urllib.request.urlretrieve(url, "cloudflared.exe")
        print("✅ cloudflared.exe downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to download cloudflared: {e}")
        return False

def start_cloudflare_tunnel():
    """Start Cloudflare tunnel and return the URL"""
    print_step("🚇", "Starting Cloudflare Tunnel...")
    
    try:
        # Start cloudflared process
        # We need to capture stderr because cloudflared prints the URL there
        process = subprocess.Popen(
            ['cloudflared.exe', 'tunnel', '--url', 'http://localhost:8000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        print("⏳ Waiting for tunnel to establish...")
        tunnel_url = None
        
        # Read stderr to find the URL
        # We give it a timeout
        start_time = time.time()
        while time.time() - start_time < 30:
            line = process.stderr.readline()
            if not line:
                if process.poll() is not None:
                    break
                continue
                
            # print(f"DEBUG: {line.strip()}") # Uncomment for debug
            
            # Look for *.trycloudflare.com
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                tunnel_url = match.group(0)
                break
                
        if tunnel_url:
            print(f"✅ Tunnel established: {tunnel_url}")
            return tunnel_url, process
        else:
            print("❌ Failed to get tunnel URL (timeout)")
            process.kill()
            return None, None
            
    except Exception as e:
        print(f"❌ Error starting tunnel: {e}")
        return None, None

def set_webhook_via_api(bot_token, webhook_url, webhook_secret):
    """Set the Telegram webhook using direct API call"""
    print_step("🔗", "Setting Telegram webhook...")
    
    full_webhook_url = f"{webhook_url}/api/v1/telegram/webhook"
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    print(f"Target: {full_webhook_url}")
    
    try:
        import json
        import urllib.request
        import urllib.error
        import ssl
        
        # Create unverified context to avoid SSL errors on some Windows machines
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        data = {
            "url": full_webhook_url,
            "secret_token": webhook_secret,
            "drop_pending_updates": True
        }
        
        req = urllib.request.Request(
            api_url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, context=ctx) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if result.get('ok'):
            print("✅ Webhook set successfully!")
            return True
        else:
            print(f"❌ Failed to set webhook: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def main():
    """Main setup and run function"""
    print_header("TELEGRAM BOT SETUP WITH CLOUDFLARE")
    
    # 0. Check Cloudflare
    if not check_cloudflared():
        return
        
    # Get bot token from user
    print_step("🔑", "Configuration")
    
    # Try to read from env first
    current_token = ""
    current_secret = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    current_token = line.split('=')[1].strip()
                elif line.startswith('TELEGRAM_WEBHOOK_SECRET='):
                    current_secret = line.split('=')[1].strip()
    
    if current_token and len(current_token) > 10:
        print(f"Found existing token: {current_token[:5]}...{current_token[-5:]}")
        use_existing = input("Use this token? (y/n): ").lower().strip()
        if use_existing == 'y':
            bot_token = current_token
        else:
            bot_token = input("Enter new Telegram bot token: ").strip()
    else:
        bot_token = input("Enter Telegram bot token: ").strip()
    
    if not bot_token:
        print("❌ Bot token is required!")
        return

    # 2. Start Cloudflare Tunnel
    tunnel_url, tunnel_process = start_cloudflare_tunnel()
    if not tunnel_url:
        return
        
    try:
        # 3. Generate Secret (or reuse) & Update .env
        if current_secret and bot_token == current_token:
            webhook_secret = current_secret
            print(f"✅ Reusing existing webhook secret")
        else:
            webhook_secret = generate_webhook_secret()
            print(f"✅ Generated webhook secret: {webhook_secret}")
            
        update_env_file(bot_token, webhook_secret, tunnel_url)
        
        # 4. Set Webhook
        if set_webhook_via_api(bot_token, tunnel_url, webhook_secret):
            print_header("🎉 SETUP COMPLETE")
        else:
            print_header("⚠️ SETUP COMPLETED WITH ERRORS")
            print("❌ Webhook setting failed (likely invalid token)")
            print("   The tunnel will be kept open for debugging.")
            
        print(f"Tunnel URL: {tunnel_url}")
        print(f"Webhook Endpoint: {tunnel_url}/api/v1/telegram/webhook")
        print("Status: Cloudflare Tunnel is RUNNING")
        print("\n📋 Next Steps:")
        print("1. Make sure your local Uvicorn server is running on port 8000")
        print("   (It should be running in another terminal window)")
        print("2. Test the bot on Telegram")
        
        print("\n⚠️  DO NOT CLOSE THIS WINDOW")
        print("   The tunnel will close if you exit this script.")
        print("   Press Ctrl+C to stop the tunnel.")
        
        # Keep alive
        try:
            while True:
                time.sleep(1)
                if tunnel_process.poll() is not None:
                    print("\n❌ Tunnel process terminated unexpectedly!")
                    break
        except KeyboardInterrupt:
            print("\n🛑 Stopping tunnel...")
        
    finally:
        if tunnel_process:
            tunnel_process.terminate()

if __name__ == "__main__":
    main()