import os
import httpx
import aiofiles
import aiofiles.tempfile # New import for asynchronous temporary files
from dotenv import load_dotenv
from services.exceptions import TranscriptionError, GPTGenerationError, TextToSpeechError
import asyncio

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

# Define the shared directory path within the container
# This must match the mount point in docker-compose.yml for both web and celery services
SHARED_AUDIO_DIR = "/tmp_shared_audio"

# Ensure the shared directory exists (good practice, though Docker usually creates it)
# This will be executed when the module is imported, ensuring the directory exists.
os.makedirs(SHARED_AUDIO_DIR, exist_ok=True)


# --- Async Transcription ---
async def transcribe_audio_async(audio_path: str) -> str:
    """
    Transcribes audio from the given path using OpenAI's Whisper model.
    Assumes audio_path is accessible within the container (e.g., from a shared volume).
    """
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            # Use aiofiles for asynchronous file reading
            async with aiofiles.open(audio_path, "rb") as audio_file:
                # Read content in chunks to avoid loading large files entirely into memory
                file_content = await audio_file.read()

                files = {"file": (os.path.basename(audio_path), file_content, "audio/webm")}
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


# --- Async GPT Completion ---
async def generate_gpt_reply_async(transcript: str) -> str:
    """
    Generates a text reply using OpenAI's GPT model based on the provided transcript.
    """
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


# --- Async TTS Generation ---
async def text_to_speech_async(text: str) -> str:
    """
    Generates speech from text using OpenAI's TTS model and saves it to a shared temporary file.
    Returns the path to the saved audio file.
    """
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
        
        # Save the TTS audio to the shared volume using aiofiles's async tempfile
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=SHARED_AUDIO_DIR) as tmp_tts_file:
            await tmp_tts_file.write(response.content)
            # Explicitly cast to str to satisfy type checker (Pylance warning)
            tts_path = str(tmp_tts_file.name) 
            
        return tts_path
    except Exception as e:
        raise TextToSpeechError(f"Error during text-to-speech generation: {e}")


# --- Synchronous wrappers for Celery tasks ---
# Celery tasks typically run synchronous functions in their worker pool,
# so these wrappers allow calling async functions from a sync context.

def transcribe_audio_sync(audio_path: str) -> str:
    """Synchronous wrapper for transcribe_audio_async."""
    return asyncio.run(transcribe_audio_async(audio_path))

def generate_gpt_reply_sync(transcript: str) -> str:
    """Synchronous wrapper for generate_gpt_reply_async."""
    return asyncio.run(generate_gpt_reply_async(transcript))

def text_to_speech_sync(text: str) -> str:
    """Synchronous wrapper for text_to_speech_async."""
    return asyncio.run(text_to_speech_async(text))

