import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler("logs/app.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
        ]
    )
    return logging.getLogger(__name__)
