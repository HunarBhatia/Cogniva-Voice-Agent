import requests
from langchain_core.tools import tool

BACKEND_URL = "http://127.0.0.1:8000/api"

# Temporary hardcoded token for testing — replace with real per-session token later
TEST_TOKEN = "TEST_TOKENeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg4NzE3ODY5LCJpYXQiOjE3ODg2MzE0NjksImp0aSI6IjZkYWIzYzVlY2VhYTQyYjNiZmU1NzlhYThjNzIzYmI1IiwidXNlcl9pZCI6IjEifQ.-e1AhHOQXUszBr8GpnCudzF3JCKJUWYci_26ex9hBYU"

@tool
def add_memory(session_id: str, fact: str) -> str:
    """Save an important fact about the patient to long-term memory."""
    resp = requests.post(
        f"{BACKEND_URL}/memory/",
        json={"fact": fact},
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    if resp.status_code == 201:
        return f"Saved to memory: {fact}"
    return f"Failed to save memory: {resp.status_code}"

@tool
def get_memory(session_id: str) -> str:
    """Retrieve saved memories/facts about this patient."""
    resp = requests.get(
        f"{BACKEND_URL}/memory/",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    if resp.status_code != 200:
        return "No memories stored yet."
    memories = [m["fact"] for m in resp.json()]
    return "\n".join(memories) if memories else "No memories stored yet."