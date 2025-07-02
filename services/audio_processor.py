import os
import tempfile
import httpx
import aiofiles
from dotenv import load_dotenv
from services.exceptions import TranscriptionError, GPTGenerationError, TextToSpeechError

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
GPT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
TTS_MODEL = os.getenv("TTS_MODEL", "tts-1")
TTS_VOICE = os.getenv("TTS_VOICE", "alloy")

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

OPENAI_BASE_URL = "https://api.openai.com/v1"

# --- Async Transcription ---
async def transcribe_audio_async(audio_path: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            with open(audio_path, "rb") as audio_file:
                files = {"file": (os.path.basename(audio_path), audio_file, "audio/webm")}
                data = {
                    "model": WHISPER_MODEL,
                    "response_format": "text"
                }
                response = await client.post(
                    f"{OPENAI_BASE_URL}/audio/transcriptions",
                    headers=HEADERS,
                    data=data,
                    files=files
                )
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        raise TranscriptionError(f"Error during transcription: {e}")

# --- Async GPT Response ---
async def generate_gpt_reply_async(transcript: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            payload = {
                "model": GPT_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": transcript}
                ]
            }
            response = await client.post(
                f"{OPENAI_BASE_URL}/chat/completions",
                headers={**HEADERS, "Content-Type": "application/json"},
                json=payload
            )
        response.raise_for_status()
        content = response.json()
        return content["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise GPTGenerationError(f"Error during GPT chat completion: {e}")

# --- Async Text-to-Speech ---
async def text_to_speech_async(text: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            payload = {
                "model": TTS_MODEL,
                "voice": TTS_VOICE,
                "input": text
            }
            response = await client.post(
                f"{OPENAI_BASE_URL}/audio/speech",
                headers={**HEADERS, "Content-Type": "application/json"},
                json=payload
            )
        response.raise_for_status()
        tts_path = tempfile.mktemp(suffix=".mp3")
        async with aiofiles.open(tts_path, "wb") as out_file:
            await out_file.write(response.content)
        return tts_path
    except Exception as e:
        raise TextToSpeechError(f"Error during text-to-speech generation: {e}")
