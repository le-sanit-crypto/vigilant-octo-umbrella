from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

def log_retry(retry_state):
    logging.warning(
        f"Retrying {retry_state.fn.__name__} due to {retry_state.outcome.exception()}, attempt {retry_state.attempt_number}"
    )

def log_error(e):
    logging.error(f"Error: {e}")

# Example retry decorator for external API calls (e.g., requests)
@retry(
    stop=stop_after_attempt(5),         # Retry up to 5 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff
    retry=retry_if_exception_type(Exception),            # Retry on any exception
    before_sleep=log_retry
)
def resilient_api_call(callable_fn, *args, **kwargs):
    try:
        return callable_fn(*args, **kwargs)
    except Exception as e:
        log_error(e)
        raise  # Needed for tenacity to catch

# Usage example:
# def fetch_market_data(...):
#     ... (requests.get or other API logic) ...
# data = resilient_api_call(fetch_market_data, ..., ...)