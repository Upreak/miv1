
import requests

URL = "http://localhost:8000/api/v1/telegram/webhook"
SECRET = "pz6stn2gnu6lk1m1688t38cc4vqqng4s"

headers = {
    "X-Telegram-Bot-Api-Secret-Token": SECRET,
    "Content-Type": "application/json"
}

data = {
    "update_id": 123456,
    "message": {
        "message_id": 1,
        "date": 1234567890,
        "chat": {"id": 123, "type": "private"},
        "text": "/start"
    }
}

try:
    print(f"Sending request to {URL} with secret {SECRET[:5]}...")
    resp = requests.post(URL, json=data, headers=headers)
    print(f"Response: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
