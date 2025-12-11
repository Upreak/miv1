# Telegram Bot Token Setup Guide

## Where to Add Your Telegram Bot Token

You have **3 easy options** to add your Telegram bot token:

## Option 1: Interactive Setup (EASIEST - Recommended) 🚀

```bash
cd Backend
python scripts/deploy_telegram_bot.py
```

This will guide you through:
1. Getting your bot token from @BotFather (if you don't have one)
2. Setting up the webhook URL
3. Generating a secure webhook secret
4. Creating the `.env` file automatically

## Option 2: Manual .env File Setup 📝

Create a file called `.env` in the `Backend/` folder with these contents:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_WEBHOOK_SECRET=YOUR_GENERATED_SECRET_HERE
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhooks/telegram

# Optional Settings (you can leave these as is for testing)
TELEGRAM_DEBUG_MODE=true
TELEGRAM_MOCK_MODE=false
TELEGRAM_RATE_LIMIT_REQUESTS=30
TELEGRAM_RATE_LIMIT_WINDOW=60
TELEGRAM_TIMEOUT=30

# Database Configuration (already working from previous fixes)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/recruitment_db
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/recruitment_db
```

### How to Get Your Bot Token:

1. **Open Telegram** and search for `@BotFather`
2. **Send this message**: `/newbot`
3. **Follow the instructions** to create your bot
4. **Copy the token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456`)
5. **Paste it** in the `.env` file above

### How to Generate Webhook Secret:

Run this command to generate a secure secret:
```bash
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32)))"
```

Copy the output and paste it as `TELEGRAM_WEBHOOK_SECRET`.

### Webhook URL Options:

For **local testing** (using ngrok or similar):
```env
TELEGRAM_WEBHOOK_URL=https://your-ngrok-url.ngrok.io/api/v1/telegram/webhooks/telegram
```

For **production**:
```env
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhooks/telegram
```

## Option 3: Environment Variables (Quick Test) ⚡

For quick testing without creating files, set environment variables:

### On Windows (Command Prompt):
```cmd
set TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
set TELEGRAM_WEBHOOK_SECRET=YOUR_SECRET_HERE
set TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhooks/telegram
```

### On Mac/Linux (Terminal):
```bash
export TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
export TELEGRAM_WEBHOOK_SECRET=YOUR_SECRET_HERE
export TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhooks/telegram
```

## Quick Test Setup (Mock Mode) 🧪

If you want to test WITHOUT a real bot token, use mock mode:

```env
TELEGRAM_BOT_TOKEN=fake_token_for_testing
TELEGRAM_WEBHOOK_SECRET=test_secret
TELEGRAM_WEBHOOK_URL=https://test.com/webhook
TELEGRAM_MOCK_MODE=true
```

This lets you test all the bot logic without needing a real Telegram bot!

## After Setting Up Token

### 1. Test the Configuration:
```bash
cd Backend
python test_telegram_bot_quick.py
```

### 2. Start Your Application:
```bash
uvicorn backend_app.main:app --reload
```

### 3. Set the Webhook:
```bash
# Using the deployment script
python scripts/deploy_telegram_bot.py

# Or manually via API
curl -X POST "https://api.telegram.org/botYOUR_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/api/v1/telegram/webhooks/telegram",
    "secret_token": "YOUR_SECRET"
  }'
```

### 4. Test Your Bot:
1. Open Telegram
2. Search for your bot (using the username @YourBotName)
3. Send these messages to test:
   - `/start` - Welcome message
   - `/help` - Help information
   - `/high` - Special greeting (as requested!)
   - "Hello" - Greeting response
   - "I'm looking for a job" - Job search assistance

## Troubleshooting Common Issues

### ❌ Token Format Error:
**Problem**: "Invalid bot token format"
**Solution**: Make sure your token looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456`

### ❌ Webhook URL Error:
**Problem**: "Invalid webhook URL format"
**Solution**: Use full URL with https://, like: `https://your-domain.com/api/v1/telegram/webhooks/telegram`

### ❌ Connection Error:
**Problem**: Can't reach webhook URL
**Solution**: 
- For local testing, use ngrok: `https://your-id.ngrok.io`
- Make sure your server is running
- Check firewall settings

### ❌ Mock Mode Testing:
**Problem**: Want to test without real bot
**Solution**: Set `TELEGRAM_MOCK_MODE=true` in your `.env` file

## Example Complete .env File

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456
TELEGRAM_WEBHOOK_SECRET=abcdefghijklmnopqrstuvwxyz123456
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhooks/telegram
TELEGRAM_DEBUG_MODE=true
TELEGRAM_MOCK_MODE=false

# Database Configuration (from previous fixes)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/recruitment_db
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/recruitment_db

# Other settings (can keep defaults)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Next Steps

1. **Choose your setup method** (Interactive, Manual .env, or Environment Variables)
2. **Add your bot token** using one of the methods above
3. **Run the test**: `python test_telegram_bot_quick.py`
4. **Start your app**: `uvicorn backend_app.main:app --reload`
5. **Test your bot** on Telegram!

Need help? Check the full documentation: `Backend/docs/TELEGRAM_BOT_GUIDE.md`