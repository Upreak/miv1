
import requests

BOT_TOKEN = "7980838931:AAGBEjbuajf8Nvy3ZSYTJ_Q9B4dXhLGJ9F8"

def get_webhook_info():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    try:
        resp = requests.get(url, timeout=10)
        print(f"Webhook Info: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_webhook_info()
