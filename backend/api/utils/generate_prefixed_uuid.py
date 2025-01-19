import uuid


def generate_prefixed_uuid(prefix: str) -> str:
    """
    Generate a UUID starting with a specific prefix.

    :param prefix: The prefix to prepend to the UUID.
    :return: A string with the format `<prefix>-<uuid>`, where the prefix is separated by a dash.
    """
    if not prefix or len(prefix) > 8:
        raise ValueError("Prefix must be non-empty and at most 8 characters.")

    # Generate a UUID with the prefix
    base_uuid = uuid.uuid4().hex  # Generate a 32-character UUID
    return f"{prefix}{base_uuid}"
