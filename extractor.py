from langchain_groq import ChatGroq
from langchain_core.tools import tool
from tools.memory import add_memory
from tools.reminders import add_reminder
from config import GROQ_API_KEY, MODEL_NAME

llm = ChatGroq(api_key=GROQ_API_KEY, model=MODEL_NAME, temperature=0)

EXTRACT_PROMPT = """Extract facts from ONE elderly dementia patient message. Nothing else — no conversation, no reasoning aloud.

For the message, identify EVERY new personal fact: names, relationships, places, feelings, events, health details, preferences, plans mentioned. Call add_memory once per distinct fact.

If a specific time-based task is mentioned (medicine, appointment, hydration, activity with a time), call add_reminder.

If there is genuinely nothing worth saving (e.g. just "hi" or "yes"), call no tools at all.

session_id: {session_id}
Message: {message}
"""

tools = [add_memory, add_reminder]
llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

def extract_and_save(session_id: str, message: str):
    prompt = EXTRACT_PROMPT.format(session_id=session_id, message=message)
    response = llm_with_tools.invoke(prompt)

    for call in response.tool_calls:
        tool_map = {"add_memory": add_memory, "add_reminder": add_reminder}
        fn = tool_map[call["name"]]
        fn.invoke({**call["args"], "session_id": session_id})