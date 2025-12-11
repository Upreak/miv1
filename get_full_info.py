
import requests
import json

BOT_TOKEN = "7980838931:AAGBEjbuajf8Nvy3ZSYTJ_Q9B4dXhLGJ9F8"

def get_info():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        print(f"URL: {data.get('result', {}).get('url')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_info()
