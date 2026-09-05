from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def speech_to_text(audio_path: str, language: str = None):
    with open(audio_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3-turbo",
            language=language,  # e.g. "hi", "bn", "ne" — or None for auto-detect
        )
    return transcription.text

if __name__ == "__main__":
    result = speech_to_text("output.mp3")  # reuse the file you just made
    print("Transcript:", result)