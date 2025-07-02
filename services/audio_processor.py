import os
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
from services.exceptions import TranscriptionError, GPTGenerationError, TextToSpeechError

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
GPT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
TTS_MODEL = os.getenv("TTS_MODEL", "tts-1")
TTS_VOICE = os.getenv("TTS_VOICE", "alloy")

client = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio(audio_path: str) -> str:
    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file,
                response_format="text"
            )
        return response.strip()
    except Exception as e:
        raise TranscriptionError(f"Error during transcription: {e}")

def generate_gpt_reply(transcript: str) -> str:
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": transcript}
            ]
        )
        message = response.choices[0].message
        if message and message.content:
            return message.content.strip()
        else:
            raise GPTGenerationError("No valid reply from GPT model.")
    except Exception as e:
        raise GPTGenerationError(f"Error during GPT chat completion: {e}")

def text_to_speech(text: str) -> str:
    try:
        speech_response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=text
        )
        tts_path = tempfile.mktemp(suffix=".mp3")
        with open(tts_path, "wb") as out_file:
            out_file.write(speech_response.content)
        return tts_path
    except Exception as e:
        raise TextToSpeechError(f"Error during text-to-speech generation: {e}")
