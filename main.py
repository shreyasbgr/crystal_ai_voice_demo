import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, BackgroundTasks # Import BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from celery import Celery
from celery.result import AsyncResult # Import AsyncResult to check task status

from services.exceptions import (
    TranscriptionError,
    GPTGenerationError,
    TextToSpeechError,
    AirtableLoggingError
)
from tasks.background_tasks import process_voice_input 
from utils.logger import setup_logger

load_dotenv()

logger = setup_logger()
app = FastAPI()

# --- Celery Configuration for the Web Application (Producer) ---
# This ensures the web app knows where to send tasks.
# It uses the REDIS_URL from your .env file (which should be redis://redis:6379/0)
# If REDIS_URL is not set in .env, it will default to the Docker Compose service name.
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Initialize a Celery app instance for the web service.
# This app is responsible for sending tasks to the broker.
# It should point to the same broker as your Celery worker.
web_celery_app = Celery(
    "voice_ai_web_tasks",  # A distinct name for the web app's Celery instance
    broker=REDIS_URL,
    backend=REDIS_URL,     # Only needed if the web app will fetch task results
)

# Serve static files (HTML, favicon, icons)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse)
async def serve_index():
    """Serves the main HTML file for the application."""
    return FileResponse("static/index.html")


@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Handles audio file uploads, saves them temporarily to a shared volume,
    and dispatches a background processing task to Celery.
    Returns the task ID immediately.
    """
    tmp_path = None
    try:
        # Define the shared directory path within the container
        # This path must match the mount point in docker-compose.yml
        SHARED_AUDIO_DIR = "/tmp_shared_audio" 
        
        # Ensure the shared directory exists (Docker usually creates it, but good practice)
        os.makedirs(SHARED_AUDIO_DIR, exist_ok=True)

        # Read the uploaded file content asynchronously
        contents = await file.read()
        
        # Use tempfile.NamedTemporaryFile with the 'dir' argument
        # This ensures the file is created directly in the shared volume
        # and tempfile handles the unique naming automatically.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm", dir=SHARED_AUDIO_DIR) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name # tmp.name will now be the full path in the shared directory
        
        logger.info(f"💾 Audio saved to temporary file: {tmp_path}")
    except Exception as e:
        logger.exception("🛑 Failed to save uploaded audio")
        raise HTTPException(status_code=400, detail="Failed to save uploaded audio")

    try:
        # Offload processing to Celery worker using the shared_task.
        # The .delay() method will use the 'web_celery_app' instance
        # that was configured above.
        result = process_voice_input.delay(tmp_path)
        logger.info(f"🚀 Task {result.id} dispatched to Celery")
        # Return the task ID so the client can poll for the result
        return JSONResponse(content={"message": "Processing started", "task_id": result.id})

    except Exception as e:
        logger.exception("❌ Failed to queue background task")
        raise HTTPException(status_code=500, detail="Failed to queue background task")


@app.get("/get-audio-response/{task_id}")
async def get_audio_response(task_id: str, background_tasks: BackgroundTasks): # Add BackgroundTasks parameter
    """
    Polls for the result of a Celery task.
    If the task is complete and successful, returns the generated TTS audio file.
    Otherwise, returns the current status or an error.
    """
    task = AsyncResult(task_id, app=web_celery_app) # Use the web_celery_app instance

    if task.ready():
        if task.successful():
            tts_file_path = task.result
            if tts_file_path and os.path.exists(tts_file_path):
                logger.info(f"✅ Task {task_id} successful. Serving audio from: {tts_file_path}")
                
                # Define the cleanup function
                def cleanup_file():
                    if os.path.exists(tts_file_path):
                        os.remove(tts_file_path)
                        logger.info(f"🗑️ Cleaned up TTS audio file: {tts_file_path}")
                
                # Add the cleanup function as a background task
                background_tasks.add_task(cleanup_file)
                
                # Return the audio file
                # Ensure media_type matches the actual audio format (e.g., "audio/mpeg" for .mp3)
                response = FileResponse(tts_file_path, media_type="audio/mpeg") 
                
                return response
            else:
                logger.error(f"❌ Task {task_id} successful but TTS file not found: {tts_file_path}")
                raise HTTPException(status_code=404, detail="AI response audio not found.")
        else:
            # Task failed
            error_message = str(task.result) if task.result else "Unknown error"
            logger.error(f"❌ Task {task_id} failed: {error_message}")
            raise HTTPException(status_code=500, detail=f"AI processing failed: {error_message}")
    else:
        # Task is still pending or started
        logger.info(f"⏳ Task {task_id} status: {task.status}")
        return JSONResponse(content={"status": task.status})


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

