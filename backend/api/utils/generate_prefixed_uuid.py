import uuid
import logging
from datetime import datetime, timezone  # Ensure correct imports

logger = logging.getLogger(__name__)


def generate_prefixed_uuid(prefix: str) -> str:
    """
    Generate a UUID starting with a specific prefix.

    :param prefix: The prefix to prepend to the UUID (max 8 characters).
    :return: A string with the format `<prefix><uuid[:8]><timestamp[:12]>` (max 36 characters).
    """
    if not prefix or len(prefix) > 8:
        raise ValueError("Prefix must be non-empty and at most 8 characters.")

    # Generate a UUID and extract the first 8 characters
    base_uuid = uuid.uuid4().hex[:8]

    # Use UTC timezone for consistent timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")  # Only 12 characters

    # Combine and ensure the result does not exceed 36 characters
    generated_id = f"{prefix}{base_uuid}{timestamp}"

    # Debug log: Generated ID
    logger.debug(f"Generated ID: {generated_id}")
    return generated_id[:36]  # Ensure the final string is not longer than 36 characters
