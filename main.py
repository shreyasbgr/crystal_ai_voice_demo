import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from services.audio_processor import (
    transcribe_audio_async,
    generate_gpt_reply_async,
    text_to_speech_async
)
from services.airtable_logger import log_to_airtable_async
from services.exceptions import (
    TranscriptionError,
    GPTGenerationError,
    TextToSpeechError,
    AirtableLoggingError
)
from utils.logger import setup_logger

logger = setup_logger()
app = FastAPI()

# Serve static files (HTML, favicon, icons)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse)
async def serve_index():
    return FileResponse("static/index.html")


@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    tmp_path = None
    try:
        # Save uploaded audio to a temporary file
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
    except Exception as e:
        logger.exception("🛑 Failed to save uploaded audio")
        raise HTTPException(status_code=400, detail="Failed to save uploaded audio")

    try:
        # Step 1: Transcribe audio
        transcript = await transcribe_audio_async(tmp_path)
        logger.info(f"🎤 Transcript: {transcript}")

        # Step 2: Generate GPT reply
        reply = await generate_gpt_reply_async(transcript)
        logger.info(f"🧠 GPT Reply: {reply}")

        # Step 3: Log to Airtable
        await log_to_airtable_async(transcript=transcript, reply=reply, lang="en", source="voice-app")
        logger.info("✅ Logged to Airtable")

        # Step 4: Convert reply to speech
        tts_path = await text_to_speech_async(reply)
        return FileResponse(tts_path, media_type="audio/mpeg", filename="response.mp3")

    except (TranscriptionError, GPTGenerationError, TextToSpeechError, AirtableLoggingError) as custom_error:
        raise custom_error  # These are already handled below

    except Exception as e:
        logger.exception("❌ Unexpected error during processing")
        raise HTTPException(status_code=500, detail="Unexpected server error")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


# --- Custom Exception Handlers ---

@app.exception_handler(TranscriptionError)
async def handle_transcription_error(request: Request, exc: TranscriptionError):
    logger.error(f"TranscriptionError: {exc}")
    return JSONResponse(status_code=500, content={"error": "Transcription failed"})

@app.exception_handler(GPTGenerationError)
async def handle_gpt_error(request: Request, exc: GPTGenerationError):
    logger.error(f"GPTGenerationError: {exc}")
    return JSONResponse(status_code=500, content={"error": "GPT response failed"})

@app.exception_handler(TextToSpeechError)
async def handle_tts_error(request: Request, exc: TextToSpeechError):
    logger.error(f"TextToSpeechError: {exc}")
    return JSONResponse(status_code=500, content={"error": "TTS generation failed"})

@app.exception_handler(AirtableLoggingError)
async def handle_airtable_error(request: Request, exc: AirtableLoggingError):
    logger.error(f"AirtableLoggingError: {exc}")
    return JSONResponse(status_code=500, content={"error": "Failed to log to Airtable"})
