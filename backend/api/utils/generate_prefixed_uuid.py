import uuid
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def generate_prefixed_uuid(prefix: str) -> str:
    """
    Generate a UUID starting with a specific prefix.

    :param prefix: The prefix to prepend to the UUID.
    :return: A string with the format `<prefix><uuid><timestamp>`.
    """
    if not prefix or len(prefix) > 8:
        raise ValueError("Prefix must be non-empty and at most 8 characters.")

    # Add a high-resolution timestamp for additional uniqueness
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")

    base_uuid = uuid.uuid4().hex
    generated_id = f"{prefix}{base_uuid[:20]}{timestamp}"

    # Debug log: Generated ID
    logger.debug(f"Generated ID: {generated_id}")
    return generated_id
