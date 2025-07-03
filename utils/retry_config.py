"""
Retry configuration utilities for network calls with exponential backoff.
"""
from httpx import Retry, Timeout


def get_default_retry_config():
    """
    Returns the default retry configuration for network calls.
    
    Returns:
        Retry: Configured retry instance with exponential backoff
    """
    return Retry(
        total=3,  # Total number of retry attempts
        backoff_factor=0.5,  # Wait 0.5 * (2 ** retry_count) seconds between attempts
        status_forcelist=[500, 502, 503, 504]  # Retry on server errors
    )


def get_default_timeout_config():
    """
    Returns the default timeout configuration for network calls.
    
    Returns:
        Timeout: Configured timeout instance
    """
    return Timeout(60, read=60)  # 60 seconds for both connect and read


def get_airtable_timeout_config():
    """
    Returns the timeout configuration for Airtable API calls.
    
    Returns:
        Timeout: Configured timeout instance with shorter timeouts for Airtable
    """
    return Timeout(30, read=30)  # 30 seconds for Airtable operations
