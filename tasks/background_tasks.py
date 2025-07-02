from celery import shared_task
from services.audio_processor import (
    transcribe_audio_sync,
    generate_gpt_reply_sync,
    text_to_speech_sync
)
from services.airtable_logger import log_to_airtable_sync
from services.exceptions import (
    TranscriptionError, GPTGenerationError,
    TextToSpeechError, AirtableLoggingError
)
import os

@shared_task
def process_voice_input(tmp_path):
    """
    Processes voice input: transcribes, generates GPT reply, logs to Airtable,
    and converts reply to speech. Cleans up temporary files.
    """
    tts_path = None # Initialize tts_path to None
    try:
        # Step 1: Transcribe audio
        transcript = transcribe_audio_sync(tmp_path)
        
        # Step 2: Generate GPT reply
        reply = generate_gpt_reply_sync(transcript)
        
        # Step 3: Log to Airtable
        log_to_airtable_sync(transcript=transcript, reply=reply, lang="en", source="voice-app")
        
        # Step 4: Convert text to speech
        tts_path = text_to_speech_sync(reply)
        
        # Return the path to the generated TTS audio file
        return tts_path
    except Exception as e:
        # Catch any exceptions during processing and re-raise as RuntimeError
        raise RuntimeError(f"Processing failed: {e}")
    finally:
        # Ensure temporary input audio file is removed
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
            # logger.info(f"Cleaned up input audio file: {tmp_path}") # Uncomment if you have logger in this file
        
        # Ensure temporary output TTS audio file is removed ONLY if it was created
        # The main.py will be responsible for serving and then deleting this file
        # once it's fetched by the client. For now, we'll let main.py handle its deletion.
        # If this task were to store results in a database, this would be the place to clean up.
