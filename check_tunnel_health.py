
import requests

TUNNEL_URL = "https://threaded-conducted-greetings-busy.trycloudflare.com"

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
    check_health()
