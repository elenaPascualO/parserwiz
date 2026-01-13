"""File validation utilities."""

import json

from backend.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE


def validate_file(content: bytes, filename: str) -> tuple[bool, str | None]:
    """Validate an uploaded file.

    Args:
        content: The file content as bytes.
        filename: The original filename.

    Returns:
        A tuple of (is_valid, error_message).
        If valid, error_message is None.
    """
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File too large. Maximum size is {max_mb:.0f}MB."

    # Check file is not empty
    if len(content) == 0:
        return False, "File is empty."

    # Check extension
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        return False, f"Invalid file type. Allowed types: {allowed}"

    return True, None


def validate_json_content(content: bytes) -> tuple[bool, str | None]:
    """Validate JSON content.

    Args:
        content: The JSON content as bytes.

    Returns:
        A tuple of (is_valid, error_message).
    """
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return False, "Invalid encoding. File must be UTF-8 encoded."

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e.msg}"

    # Check that it's an array of objects or an object with array values
    if isinstance(data, list):
        if not data:
            return False, "JSON array is empty."
        if not all(isinstance(item, dict) for item in data):
            return False, "JSON array must contain objects."
    elif isinstance(data, dict):
        # Check if it's a single object or has array values
        if not data:
            return False, "JSON object is empty."
    else:
        return False, "JSON must be an array of objects or an object."

    return True, None
