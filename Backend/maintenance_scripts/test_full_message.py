
import requests
import json
import time

URL = "http://localhost:8000/api/v1/telegram/webhook"
SECRET = "pz6stn2gnu6lk1m1688t38cc4vqqng4s"

headers = {
    "X-Telegram-Bot-Api-Secret-Token": SECRET,
    "Content-Type": "application/json"
}

# Realistic payload
payload = {
    "update_id": 999999,
    "message": {
        "message_id": 1,
        "from": {
            "id": 123456789,
            "is_bot": False,
            "first_name": "Test",
            "username": "testuser",
            "language_code": "en"
        },
        "chat": {
            "id": 123456789,
            "first_name": "Test",
            "username": "testuser",
            "type": "private"
        },
        "date": int(time.time()),
        "text": "Hi"
    }
}

try:
    print(f"Sending payload to {URL}...")
    resp = requests.post(URL, json=payload, headers=headers)
    print(f"Response: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
