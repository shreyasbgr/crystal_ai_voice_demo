import requests
import datetime
import uuid
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME

def log_to_airtable(transcript: str, reply: str, lang: str = "auto", source: str = "voice-app") -> bool:
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    record_id = str(uuid.uuid4())  # Generate a unique ID

    payload = {
        "fields": {
            "Record ID": record_id,  # Primary field
            "Timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "Transcript": transcript,
            "GPT Reply": reply,
            "Language": lang,
            "Source": source
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code not in (200, 201):
        print(f"❌ Failed to log to Airtable: {response.status_code}, {response.text}")
        return False

    print(f"✅ Successfully logged to Airtable with Record ID: {record_id}")
    return True
