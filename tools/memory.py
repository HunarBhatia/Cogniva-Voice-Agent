import json
from langchain_core.tools import tool

DB_PATH="mock_db.json"
def _load():
    with open(DB_PATH, "r") as f:
        return json.load(f)

def _save(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

@tool
def add_memory(session_id: str, fact: str) -> str:
    """Save an important fact about the patient (routine, preference, event) to long-term memory."""
    data = _load()
    data.setdefault(session_id, {}).setdefault("memories", []).append(fact)
    _save(data)
    return f"Saved to memory: {fact}"

@tool
def get_memory(session_id: str) -> str:
    """Retrieve saved memories/facts about this patient."""
    data = _load()
    memories = data.get(session_id, {}).get("memories", [])
    return "\n".join(memories) if memories else "No memories stored yet."
