import tempfile
import os
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, WHISPER_MODEL, TTS_MODEL, TTS_VOICE

client = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio_file,
            response_format="text"
        )
    return result.strip()

def generate_gpt_reply(transcript: str) -> str:
    chat_response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": transcript},
        ]
    )
    choice = chat_response.choices[0]
    return choice.message.content.strip() if choice.message and choice.message.content else \
           "Sorry, I couldn’t understand that. Please try again."

def text_to_speech(reply_text: str) -> str:
    speech_response = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=reply_text
    )

    tts_path = tempfile.mktemp(suffix=".mp3")
    with open(tts_path, "wb") as out_file:
        out_file.write(speech_response.content)
    return tts_path
