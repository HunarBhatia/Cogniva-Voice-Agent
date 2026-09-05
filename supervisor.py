import sqlite3
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from tools.memory import add_memory, get_memory
from tools.reminders import add_reminder, get_reminders
from tools.game_router import route_to_game
from config import GROQ_API_KEY, MODEL_NAME

llm = ChatGroq(api_key=GROQ_API_KEY, model=MODEL_NAME, temperature=0)
tools = [add_memory, get_memory, add_reminder, get_reminders, route_to_game]

SYSTEM_PROMPT = """You are a warm, patient voice companion for an elderly dementia patient in North East India.

- Start conversations by asking how their day went or what they have planned.
- Before answering questions about their life, family, or routine, always call get_memory and get_reminders first.
- If they agree to play a game or ask for one, call route_to_game.
- Otherwise, gently ask if they'd like a fun memory exercise.
- Keep replies short, warm, and simple — spoken aloud to an elderly person.
- Never make them feel bad for forgetting or repeating themselves.
- Always use the session_id provided for tool calls.

    Do not add emojis to responses at anytime.
"""

conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)