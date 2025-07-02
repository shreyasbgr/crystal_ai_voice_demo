import httpx
import datetime
import uuid
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME
from services.exceptions import AirtableLoggingError

async def log_to_airtable_async(transcript: str, reply: str, lang: str = "auto", source: str = "voice-app") -> None:
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    record_id = str(uuid.uuid4())
    payload = {
        "fields": {
            "Record ID": record_id,
            "Timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "Transcript": transcript,
            "GPT Reply": reply,
            "Language": lang,
            "Source": source
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.RequestError as e:
        raise AirtableLoggingError(f"Network error during Airtable logging: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise AirtableLoggingError(f"Airtable API error: {str(e)}")

    print(f"✅ Successfully logged to Airtable with Record ID: {record_id}")
