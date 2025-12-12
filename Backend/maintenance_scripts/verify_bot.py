
import requests
import time
import sys

BOT_TOKEN = "7980838931:AAGBEjbuajf8Nvy3ZSYTJ_Q9B4dXhLGJ9F8"
WEBHOOK_SECRET = "pz6stn2gnu6lk1m1688t38ccc4vqqng4s"
TUNNEL_URL = "https://threaded-conducted-greetings-busy.trycloudflare.com"

def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    payload = {
        "url": f"{TUNNEL_URL}/api/v1/telegram/webhook",
        "secret_token": WEBHOOK_SECRET,
        "drop_pending_updates": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Set Webhook: {resp.status_code} {resp.text}")
        return resp.ok
    except Exception as e:
        print(f"Set Webhook Error: {e}")
        return False

def check_health():
    url = f"{TUNNEL_URL}/api/v1/telegram/health"
    print(f"Checking health at {url}...")
    try:
        resp = requests.get(url, timeout=10)
        print(f"Health Check: {resp.status_code} {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Health Check Error: {e}")
        return False

if __name__ == "__main__":
    if set_webhook():
        print("Webhook set successfully.")
        # Wait a bit for propagation?
        time.sleep(2)
        if check_health():
            print("Health check passed!")
        else:
            print("Health check failed.")
            sys.exit(1)
    else:
        print("Failed to set webhook.")
        sys.exit(1)
