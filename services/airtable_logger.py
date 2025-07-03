import httpx
import datetime
import uuid
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME
from services.exceptions import AirtableLoggingError
from utils.retry_config import get_default_retry_config, get_airtable_timeout_config, retry_async_request

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

    async def _make_request():
        timeout = get_airtable_timeout_config()
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response
    
    try:
        retry_config = get_default_retry_config()
        await retry_async_request(_make_request, retry_config)
    except httpx.RequestError as e:
        raise AirtableLoggingError(f"Network error during Airtable logging: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise AirtableLoggingError(f"Airtable API error: {str(e)}")

    print(f"✅ Successfully logged to Airtable with Record ID: {record_id}")
