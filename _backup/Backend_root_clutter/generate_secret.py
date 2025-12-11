#!/usr/bin/env python3
"""
Generate Webhook Secret for Telegram Bot
"""

import secrets

def generate_secret():
    """Generate a secure webhook secret"""
    secret = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))
    return secret

def update_telegram_env(secret):
    """Update the .env.telegram file with the generated secret"""
    print("📝 Updating .env.telegram file...")
    
    # Read current .env.telegram file
    with open('.env.telegram', 'r') as f:
        content = f.read()
    
    # Update webhook secret
    content = content.replace('YOUR_GENERATED_SECRET_HERE', secret)
    
    # Write back
    with open('.env.telegram', 'w') as f:
        f.write(content)
    
    print(f"✅ Updated .env.telegram with webhook secret: {secret}")

def main():
    """Main function"""
    print("🔐 Generating webhook secret...")
    
    secret = generate_secret()
    print(f"✅ Generated secret: {secret}")
    
    update_telegram_env(secret)
    
    print("\n📋 Configuration Summary:")
    print(f"   Bot Token: 7980838931:AAFGLKKsdt_E3YjXA1Ula7r3YUFPxY22YD0")
    print(f"   Webhook Secret: {secret}")
    print(f"   Webhook URL: https://00d7585dd459.ngrok-free.app/api/v1/telegram/webhooks/telegram")
    
    print("\n🚀 Next Steps:")
    print("1. Start your FastAPI application:")
    print("   uvicorn backend_app.main:app --reload")
    print("\n2. Set the webhook:")
    print("   python scripts/deploy_telegram_bot.py --non-interactive")
    print("\n3. Test your bot on Telegram:")
    print("   - Send /high")
    print("   - Send /start")
    print("   - Send /help")

if __name__ == "__main__":
    main()