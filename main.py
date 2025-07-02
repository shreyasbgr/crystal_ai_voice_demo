import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from services.audio_processor import transcribe_audio, generate_gpt_reply, text_to_speech
from services.airtable_logger import log_to_airtable
from utils.logger import setup_logger
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

logger = setup_logger()
app = FastAPI()

# Mount static folder (if not already done)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html") as f:
        return f.read()
    
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    # Save uploaded audio to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Step 1: Transcribe audio
        transcript = transcribe_audio(tmp_path)
        logger.info(f"🎤 Transcript: {transcript}")

        # Step 2: Generate GPT reply
        reply = generate_gpt_reply(transcript)
        logger.info(f"🧠 GPT Reply: {reply}")

        # Step 3: Log to Airtable
        if log_to_airtable(transcript=transcript, reply=reply, lang="en", source="voice-app"):
            logger.info("✅ Successfully logged to Airtable")
        else:
            logger.warning("⚠️ Failed to log to Airtable")

        # Step 4: Generate speech response
        tts_path = text_to_speech(reply)
        return FileResponse(tts_path, media_type="audio/mpeg", filename="response.mp3")

    finally:
        # Clean up temp file
        os.remove(tmp_path)
