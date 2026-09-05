import requests

BACKEND_URL = "http://127.0.0.1:8000/api"

# Set per request by server.py; falls back to auto-login for terminal testing
_current_token = None

def set_token(token: str):
    global _current_token
    if token:
        _current_token = token

def get_token() -> str:
    global _current_token
    if _current_token:
        return _current_token
    # fallback: log in as test user so main.py works without a frontend
    resp = requests.post(
        f"{BACKEND_URL}/login/",
        json={"username": "testpatient", "password": "testpass123"},
    )
    _current_token = resp.json()["access"]
    return _current_token

def auth_headers():
    return {"Authorization": f"Bearer {get_token()}"}