# exceptions.py

class TranscriptionError(Exception):
    """Raised when audio transcription fails"""
    pass

class GPTGenerationError(Exception):
    """Raised when GPT reply generation fails"""
    pass

class TextToSpeechError(Exception):
    """Raised when TTS generation fails"""
    pass

class AirtableLoggingError(Exception):
    """Raised when logging to Airtable fails"""
    pass
