import os
import tempfile
import httpx
import aiofiles
from config import (
    OPENAI_API_KEY, 
    WHISPER_MODEL, 
    OPENAI_MODEL as GPT_MODEL, 
    TTS_MODEL, 
    TTS_VOICE, 
    OPENAI_BASE_URL
)
from services.exceptions import TranscriptionError, GPTGenerationError, TextToSpeechError
from utils.retry_config import get_default_retry_config, get_default_timeout_config, retry_async_request

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}



# --- Async Transcription ---
async def transcribe_audio_async(audio_path: str, client: httpx.AsyncClient) -> str:
    async def _make_request():
        timeout = get_default_timeout_config()
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
                files=files,
                timeout=timeout
            )
            response.raise_for_status()
            return response.text.strip()
    
    try:
        retry_config = get_default_retry_config()
        return await retry_async_request(_make_request, retry_config)
    except Exception as e:
        raise TranscriptionError(f"Error during transcription: {e}")

# --- Async GPT Response ---
async def generate_gpt_reply_async(transcript: str, client: httpx.AsyncClient) -> str:
    async def _make_request():
        timeout = get_default_timeout_config()
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
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        content = response.json()
        return content["choices"][0]["message"]["content"].strip()
    
    try:
        retry_config = get_default_retry_config()
        return await retry_async_request(_make_request, retry_config)
    except Exception as e:
        raise GPTGenerationError(f"Error during GPT chat completion: {e}")

# --- Async Text-to-Speech ---
async def text_to_speech_async(text: str, client: httpx.AsyncClient) -> str:
    async def _make_request():
        timeout = get_default_timeout_config()
        payload = {
            "model": TTS_MODEL,
            "voice": TTS_VOICE,
            "input": text
        }
        response = await client.post(
            f"{OPENAI_BASE_URL}/audio/speech",
            headers={**HEADERS, "Content-Type": "application/json"},
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        tts_path = tempfile.mktemp(suffix=".mp3")
        async with aiofiles.open(tts_path, "wb") as out_file:
            await out_file.write(response.content)
        return tts_path
    
    try:
        retry_config = get_default_retry_config()
        return await retry_async_request(_make_request, retry_config)
    except Exception as e:
        raise TextToSpeechError(f"Error during text-to-speech generation: {e}")
