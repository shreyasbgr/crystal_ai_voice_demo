"""
Retry configuration utilities for network calls with exponential backoff.
"""
import asyncio
import httpx
from typing import Callable, Any, List


class RetryConfig:
    """Configuration for retry logic with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 0.5, 
                 retry_status_codes: List[int] = None):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_status_codes = retry_status_codes or [500, 502, 503, 504]


async def retry_async_request(func: Callable, retry_config: RetryConfig, *args, **kwargs) -> Any:
    """
    Execute an async function with retry logic and exponential backoff.
    
    Args:
        func: The async function to execute
        retry_config: Retry configuration
        *args, **kwargs: Arguments to pass to the function
    
    Returns:
        The result of the function call
    
    Raises:
        The last exception if all retries are exhausted
    """
    last_exception = None
    
    for attempt in range(retry_config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as e:
            last_exception = e
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code not in retry_config.retry_status_codes:
                raise

            if attempt < retry_config.max_retries:
                wait_time = retry_config.backoff_factor * (2 ** attempt)
                await asyncio.sleep(wait_time)
            else:
                raise
    
    # If we get here, all retries were exhausted
    raise last_exception


def get_default_retry_config() -> RetryConfig:
    """
    Returns the default retry configuration for network calls.
    
    Returns:
        RetryConfig: Configured retry instance with exponential backoff
    """
    return RetryConfig(
        max_retries=3,
        backoff_factor=0.5,
        retry_status_codes=[500, 502, 503, 504]
    )


def get_default_timeout_config() -> httpx.Timeout:
    """
    Returns the default timeout configuration for network calls.
    
    Returns:
        httpx.Timeout: Configured timeout instance
    """
    return httpx.Timeout(60.0)


def get_airtable_timeout_config() -> httpx.Timeout:
    """
    Returns the timeout configuration for Airtable API calls.
    
    Returns:
        httpx.Timeout: Configured timeout instance with shorter timeouts for Airtable
    """
    return httpx.Timeout(30.0)
