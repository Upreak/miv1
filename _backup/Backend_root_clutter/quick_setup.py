#!/usr/bin/env python3
"""
Quick Setup Script for Telegram Bot
Automates the remaining setup steps
"""

import os
import sys
import subprocess
import time

def generate_webhook_secret():
    """Generate a secure webhook secret"""
    import secrets
    secret = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))
    return secret

def update_env_file(secret, ngrok_url):
    """Update the .env file with webhook secret and URL"""
    print("📝 Updating .env file...")
    
    # Read current .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Update webhook secret
    content = content.replace('YOUR_GENERATED_SECRET_HERE', secret)
    
    # Update webhook URL (it should already be updated, but let's make sure)
    content = content.replace('https://00d7585dd459.ngrok-free.app/api/v1/telegram/webhooks/telegram', ngrok_url)
    
    # Write back
    with open('.env', 'w') as f:
        f.write(content)
    
    print(f"✅ Updated .env file with webhook secret and URL")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Main requirements installed")
        
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend_app/requirements.txt'], check=True)
        print("✅ Backend app requirements installed")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    return True

def test_configuration():
    """Test the configuration"""
    print("🧪 Testing configuration...")
    
    try:
        result = subprocess.run([sys.executable, 'test_telegram_bot_quick.py'], check=True)
        print("✅ Configuration test passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Telegram Bot Quick Setup")
    print("=" * 50)
    
    # Step 1: Generate webhook secret
    print("🔐 Generating webhook secret...")
    secret = generate_webhook_secret()
    print(f"✅ Generated secret: {secret}")
    
    # Step 2: Get ngrok URL from user
    ngrok_url = "https://00d7585dd459.ngrok-free.app/api/v1/telegram/webhooks/telegram"
    print(f"🌐 Using ngrok URL: {ngrok_url}")
    
    # Step 3: Update .env file
    update_env_file(secret, ngrok_url)
    
    # Step 4: Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return
    
    # Step 5: Test configuration
    if not test_configuration():
        print("❌ Setup failed during configuration test")
        return
    
    print("\n" + "=" * 50)
    print("🎉 Quick Setup Complete!")
    print("=" * 50)
    
    print("\n📋 Next Steps:")
    print("1. Start your FastAPI application:")
    print("   uvicorn backend_app.main:app --reload")
    print("\n2. In a new terminal, set the webhook:")
    print("   python scripts/deploy_telegram_bot.py")
    print("   (Choose 'Non-interactive mode')")
    print("\n3. Test your bot on Telegram:")
    print("   - Send /high")
    print("   - Send /start")
    print("   - Send /help")
    
    print("\n📖 For detailed instructions, see:")
    print("   Backend/REAL_BOT_SETUP_GUIDE.md")
    
    print(f"\n🔧 Your webhook URL:")
    print(f"   {ngrok_url}")
    
    print(f"\n🔐 Your webhook secret:")
    print(f"   {secret}")
    
    print("\n🎯 Your bot is ready to test!")

if __name__ == "__main__":
    main()