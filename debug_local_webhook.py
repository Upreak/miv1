
import requests
import json

payload = {
    "update_id": 10000,
    "message": {
        "message_id": 1111,
        "from": {
            "id": 123456789,
            "is_bot": False,
            "first_name": "Test",
            "username": "test_user"
        },
        "chat": {
            "id": 123456789,
            "first_name": "Test",
            "username": "test_user",
            "type": "private"
        },
        "date": 1678900000,
        "text": "/start"
    }
}

headers = {
    "Content-Type": "application/json",
    "X-Telegram-Bot-Api-Secret-Token": "tk0v7615n0lizdvtybdo1fr0223907wm"
}

try:
    resp = requests.post("http://localhost:8000/api/v1/telegram/webhooks/telegram", json=payload, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
