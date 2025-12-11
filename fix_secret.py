
import requests

# CONSTANTS from .env
BOT_TOKEN = "7980838931:AAGBEjbuajf8Nvy3ZSYTJ_Q9B4dXhLGJ9F8"
WEBHOOK_SECRET = "pz6stn2gnu6lk1m1688t38cc4vqqng4s"
# Note: Using the route verified in previous step (/api/v1/telegram/webhook)
WEBHOOK_URL = "https://threaded-conducted-greetings-busy.trycloudflare.com/api/v1/telegram/webhook"

def fix_webhook():
    print(f"Setting webhook...")
    print(f"URL: {WEBHOOK_URL}")
    print(f"Secret: {WEBHOOK_SECRET}")
    
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    
    params = {
        "url": WEBHOOK_URL,
        "secret_token": WEBHOOK_SECRET,
        "drop_pending_updates": True
    }
    
    try:
        resp = requests.post(api_url, params=params)
        print(f"Response Code: {resp.status_code}")
        print(f"Response Body: {resp.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_webhook()
