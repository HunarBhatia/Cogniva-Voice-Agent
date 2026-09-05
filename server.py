import os
import uuid
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from concurrent.futures import ThreadPoolExecutor
import asyncio

from nodes.stt import speech_to_text
from nodes.tts import text_to_speech
from supervisor import agent
from extractor import extract_and_save

app = FastAPI()
executor = ThreadPoolExecutor(max_workers=2)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("audio_out", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio_out"), name="audio")

LOCALE_MAP = {"hi-IN": "hi", "hi": "hi", "en-US": "en", "en": "en"}
VOICE_MAP = {"hi": "hi-IN-SwaraNeural", "en": "en-IN-NeerjaNeural"}

@app.post("/voice-turn")
async def voice_turn(
    transcript: str = Form(""),
    locale: str = Form("en-US"),
    route: str = Form(""),
    sessionId: str = Form(...),
    token: str = Form(""),
    audio: UploadFile = None,
):
    lang = LOCALE_MAP.get(locale, "en")
    session_id = sessionId

    # If audio provided, transcribe it ourselves (overrides browser transcript)
    final_transcript = transcript
    if audio is not None:
        temp_path = f"audio_out/in_{uuid.uuid4().hex}.webm"
        with open(temp_path, "wb") as f:
            f.write(await audio.read())
        try:
            final_transcript = speech_to_text(temp_path, language=lang)
        except Exception:
            pass  # fall back to browser transcript if STT fails
        finally:
            os.remove(temp_path)

    config = {"configurable": {"thread_id": session_id}}

    extract_future = executor.submit(extract_and_save, session_id, final_transcript)
    reply_future = executor.submit(
        agent.invoke,
        {"messages": [("user", f"[session_id: {session_id}] {final_transcript}")]},
        config,
    )
    result = reply_future.result()
    extract_future.result()

    reply_text = result["messages"][-1].content

    intent = "CHAT"
    game_command = None
    if "[ROUTED_TO_GAME" in reply_text or any(
        "route_to_game" in str(m) for m in result["messages"]
    ):
        intent = "START_GAME"
        game_command = {
            "action": "START_GAME",
            "gameId": "memory-garden-match",
            "source": "voice",
            "transcript": final_transcript,
        }

    audio_filename = f"out_{uuid.uuid4().hex}.mp3"
    audio_path = f"audio_out/{audio_filename}"
    voice = VOICE_MAP.get(lang, "en-IN-NeerjaNeural")
    await text_to_speech(reply_text, voice, audio_path)

    return JSONResponse({
        "replyText": reply_text,
        "replyAudioUrl": f"http://localhost:8001/audio/{audio_filename}",
        "intent": intent,
        "gameCommand": game_command,
    })  