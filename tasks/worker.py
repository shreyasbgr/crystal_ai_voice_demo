# tasks/worker.py

from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "voice_ai_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    # Explicitly include the module where your tasks are defined.
    # This ensures Celery knows to load and register tasks from this file.
    include=['tasks.background_tasks']
)
celery_app.conf.task_track_started = True

# The autodiscover_tasks line can remain, but 'include' provides a more direct
# way to ensure specific task modules are loaded.
# celery_app.autodiscover_tasks(["tasks"]) # This line is now less critical but can stay

