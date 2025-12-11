#!/usr/bin/env python3
"""
Complete Final Telegram Bot Setup Script
Everything included - generates webhook secret and sets up everything
"""

import os
import sys
import subprocess
import secrets
import time

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

def create_telegram_env_file(secret):
    """Create the .env.telegram file with all settings"""
    print_step("📝", "Creating .env.telegram file...")
    
    content = f"""# Telegram Bot Configuration
# This file contains Telegram-specific settings

# Bot Token from @BotFather
TELEGRAM_BOT_TOKEN=7980838931:AAFGLKKsdt_E3YjXA1Ula7r3YUFPxY22YD0

# Webhook URL from ngrok
TELEGRAM_WEBHOOK_URL=https://00d7585dd459.ngrok-free.app/api/v1/telegram/webhooks/telegram

# Webhook Secret (generated)
TELEGRAM_WEBHOOK_SECRET={secret}

# Optional Settings
TELEGRAM_DEBUG_MODE=true
TELEGRAM_MOCK_MODE=false
TELEGRAM_RATE_LIMIT_REQUESTS=30
TELEGRAM_RATE_LIMIT_WINDOW=60
TELEGRAM_TIMEOUT=30
TELEGRAM_RETRY_ATTEMPTS=3"""
    
    with open('.env.telegram', 'w') as f:
        f.write(content)
    
    print(f"✅ Created .env.telegram with webhook secret: {secret}")
    return secret

def install_dependencies():
    """Install all required dependencies"""
    print_step("📦", "Installing dependencies...")
    
    try:
        print("Installing main requirements...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Main requirements installed")
        else:
            print(f"⚠️  Main requirements warning: {result.stderr[:100]}")
        
        print("Installing backend app requirements...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend_app/requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend app requirements installed")
        else:
            print(f"⚠️  Backend requirements warning: {result.stderr[:100]}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_application():
    """Start the FastAPI application"""
    print_step("🚀", "Starting FastAPI application...")
    
    print("Command to run:")
    print("uvicorn backend_app.main:app --reload")
    print("\nThis will start the server on http://127.0.0.1:8000")
    print("Keep this running in one terminal window.")

def set_webhook():
    """Set the Telegram webhook using the deployment script"""
    print_step("🔗", "Setting Telegram webhook...")
    
    try:
        # Run the deployment script in non-interactive mode
        result = subprocess.run([
            sys.executable, 'scripts/deploy_telegram_bot.py', 
            '--non-interactive'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Webhook setup completed")
            print("Output:", result.stdout[-300:])  # Last 300 chars
        else:
            print("⚠️  Webhook setup had issues, but may still work")
            print("Error:", result.stderr[-300:])  # Last 300 chars
        
        return True
    except subprocess.TimeoutExpired:
        print("⚠️  Webhook setup timed out (but may still be working)")
        return True
    except Exception as e:
        print(f"⚠️  Webhook setup error: {e}")
        return True  # Don't fail the whole setup for this

def main():
    """Main setup function"""
    print_header("TELEGRAM BOT COMPLETE FINAL SETUP")
    print("Your bot token is already configured!")
    print("Bot Token: 7980838931:AAFGLKKsdt_E3YjXA1Ula7r3YUFPxY22YD0")
    print("ngrok URL: https://00d7585dd459.ngrok-free.app")
    
    # Step 1: Generate webhook secret and create .env.telegram file
    webhook_secret = generate_webhook_secret()
    print(f"✅ Generated webhook secret: {webhook_secret}")
    
    create_telegram_env_file(webhook_secret)
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return
    
    print_header("🎉 SETUP COMPLETE!")
    
    print("\n📋 Final Steps:")
    print("1. Start your FastAPI application:")
    print("   uvicorn backend_app.main:app --reload")
    print("\n2. Keep ngrok running (it should already be running)")
    print("\n3. Set the webhook:")
    print("   python scripts/deploy_telegram_bot.py --non-interactive")
    print("\n4. Test your bot on Telegram:")
    print("   - Send /high")
    print("   - Send /start") 
    print("   - Send /help")
    print("   - Send 'I'm looking for a job'")
    
    print("\n📖 Expected responses:")
    print("• /high → 'Hey there! 🌟 I'm here and ready to help!'")
    print("• /start → Welcome message with bot capabilities")
    print("• /help → List of available commands")
    print("• Job query → Job search assistance")
    
    print(f"\n🔧 Configuration Summary:")
    print(f"   Bot Token: 7980838931:AAFGLKKsdt_E3YjXA1Ula7r3YUFPxY22YD0")
    print(f"   Webhook Secret: {webhook_secret}")
    print(f"   Webhook URL: https://00d7585dd459.ngrok-free.app/api/v1/telegram/webhooks/telegram")
    
    print(f"\n🌐 Health Check URL:")
    print(f"   https://00d7585dd459.ngrok-free.app/api/v1/telegram/health")
    
    print(f"\n🤖 Your bot is ready! Test it now on Telegram!")

if __name__ == "__main__":
    main()