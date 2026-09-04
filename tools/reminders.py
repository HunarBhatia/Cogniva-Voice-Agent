import json
from langchain_core.tools import tool

DB_PATH = "mock_db/session_data.json"

def _load():
    with open(DB_PATH, "r") as f:
        return json.load(f)

def _save(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

@tool
def add_reminder(session_id: str, reminder: str, time: str) -> str:
    """Add a reminder for medicine, hydration, activity, or appointment."""
    data = _load()
    data.setdefault(session_id, {}).setdefault("reminders", []).append({"text": reminder, "time": time})
    _save(data)
    return f"Reminder set: {reminder} at {time}"

@tool
def get_reminders(session_id: str) -> str:
    """Get all pending reminders for this patient."""
    data = _load()
    reminders = data.get(session_id, {}).get("reminders", [])
    if not reminders:
        return "No reminders set."
    return "\n".join([f"{r['text']} at {r['time']}" for r in reminders])