# Real Bot Setup Guide - Complete Instructions

## 🎉 You're Ready to Go!

You've already:
✅ Created a Telegram bot  
✅ Added the bot token to `.env` file  

Now let's complete the setup!

## 🔐 Generate Webhook Secret (Python Command)

Run this command in your terminal to generate a secure webhook secret:

### **Windows Command Prompt:**
```cmd
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32)))"
```

### **Mac/Linux Terminal:**
```bash
python3 -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32)))"
```

### **Expected Output:**
```
a7b3c9d2e5f8g1h4i6j9k2l7m0n3o5p8
```

**Copy this output** - this is your webhook secret!

## 📝 Update Your `.env` File

Edit your `Backend/.env` file and update these lines:

```env
# Change this line:
TELEGRAM_WEBHOOK_SECRET=YOUR_GENERATED_SECRET_HERE
# To:
TELEGRAM_WEBHOOK_SECRET=a7b3c9d2e5f8g1h4i6j9k2l7m0n3o5p8
```

*(Replace with the secret you generated)*

## 🌐 Set Up Webhook URL

### **Option A: Local Testing (Recommended for now)**

1. **Download ngrok** from [ngrok.com](https://ngrok.com/)
2. **Install and run:**
   ```bash
   ngrok http 8000
   ```
3. **Copy the generated URL** (looks like `https://abc123def456.ngrok.io`)
4. **Update your `.env` file:**
   ```env
   # Change this line:
   TELEGRAM_WEBHOOK_URL=YOUR_WEBHOOK_URL_HERE
   # To:
   TELEGRAM_WEBHOOK_URL=https://abc123def456.ngrok.io/api/v1/telegram/webhooks/telegram
   ```

### **Option B: Production (if you have a domain)**

```env
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhooks/telegram
```

## 🚀 Start Testing!

### **Step 1: Install Dependencies**
```bash
cd Backend
pip install -r requirements.txt
pip install -r backend_app/requirements.txt
```

### **Step 2: Test Configuration**
```bash
python test_telegram_bot_quick.py
```

### **Step 3: Start Your Application**
```bash
uvicorn backend_app.main:app --reload
```

### **Step 4: Set Webhook**
```bash
# Using the deployment script
python scripts/deploy_telegram_bot.py
```

When prompted, choose **"Non-interactive mode"** since you already have the token configured.

### **Step 5: Test Your Bot on Telegram**

1. **Open Telegram** and search for your bot (using the username @YourBotName)
2. **Send these messages to test:**
   - `/start` - Welcome message
   - `/help` - Help information
   - `/high` - **Special greeting** (as requested!)
   - "Hello" - Greeting response
   - "I'm looking for a job" - Job search assistance

## 🔍 Expected Responses

### **`/high` Command Response:**
```
Hey there! 🌟 I'm here and ready to help!

Whether you're looking for:
• Exciting job opportunities
• Resume improvements
• Career guidance
• Or just have questions

I've got you covered! What can I help you with today?
```

### **`/start` Command Response:**
```
Welcome to our recruitment bot, [Your Name]! 🎉

I'm here to help you with your job search. Here's what I can do:

📋 Job Search: Find matching positions
📄 Resume Analysis: Upload and get feedback
💡 Career Advice: Get guidance
🚀 Application Help: Direct assistance

Type /help to see all options or start by telling me what you're looking for!
```

### **`/help` Command Response:**
```
Here are the commands I understand:

/start - Start conversation
/help - Show this help
/high - Special greeting

You can also:
• Upload your resume (PDF/DOCX)
• Ask about job opportunities
• Request career advice
• Search for specific positions

How can I help you today?
```

## 🧪 Quick Test Commands

Test your bot setup:

```bash
# Test 1: Check if bot is responding
curl -X GET "https://api.telegram.org/botYOUR_TOKEN/getMe"

# Expected response:
# {"ok":true,"result":{"id":123456789,"is_bot":true,"first_name":"YourBot","username":"YourBot"}}

# Test 2: Check webhook info
curl -X GET "https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo"

# Expected response should show your webhook URL
```

## 🔧 Troubleshooting

### **Problem: Bot not responding**
**Solution:**
1. Check that your ngrok URL is accessible in browser
2. Verify webhook is set: `curl -X GET "https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo"`
3. Check application logs for errors

### **Problem: Webhook URL not accessible**
**Solution:**
1. Make sure ngrok is running
2. Check that your FastAPI app is running on port 8000
3. Verify firewall settings

### **Problem: Invalid webhook secret**
**Solution:**
1. Regenerate secret with the Python command
2. Update `.env` file
3. Restart your application

### **Problem: Token validation error**
**Solution:**
1. Verify token format: `123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456`
2. Check `.env` file has correct token
3. Restart application

## 📋 Final Checklist

- [ ] Generated webhook secret with Python command
- [ ] Updated `TELEGRAM_WEBHOOK_SECRET` in `.env`
- [ ] Set up ngrok and updated `TELEGRAM_WEBHOOK_URL`
- [ ] Installed dependencies
- [ ] Started FastAPI application
- [ ] Set webhook using deployment script
- [ ] Tested bot commands on Telegram

## 🎉 You're All Set!

Once you complete these steps, your Telegram bot will be fully functional with:
- ✅ Intelligent responses to all commands
- ✅ Special "/high" command response
- ✅ Job search assistance
- ✅ Resume analysis capabilities
- ✅ Career guidance
- ✅ Production-ready security and monitoring

**Need help?** Check the full documentation: `Backend/docs/TELEGRAM_BOT_GUIDE.md`