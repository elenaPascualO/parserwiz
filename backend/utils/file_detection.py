"""File type detection utilities."""

import json
from pathlib import Path


def detect_file_type(content: bytes, filename: str) -> str | None:
    """Detect file type by content and filename.

    Attempts to detect the file type by examining the content first,
    then falls back to the file extension.

    Args:
        content: The file content as bytes.
        filename: The original filename.

    Returns:
        The detected file type ('json', 'csv', 'xlsx', 'xls') or None if unknown.
    """
    # Try to detect by content first
    detected = _detect_by_content(content)
    if detected:
        return detected

    # Fall back to extension
    return _detect_by_extension(filename)


def _detect_by_content(content: bytes) -> str | None:
    """Detect file type by examining content.

    Args:
        content: The file content as bytes.

    Returns:
        The detected file type or None.
    """
    # Check for Excel formats by magic bytes
    # XLSX files start with PK (ZIP format)
    if content[:4] == b"PK\x03\x04":
        return "xlsx"

    # XLS files start with D0 CF 11 E0 (OLE format)
    if content[:4] == b"\xd0\xcf\x11\xe0":
        return "xls"

    # Try to decode as text for JSON/CSV detection
    try:
        text = content.decode("utf-8").strip()
    except UnicodeDecodeError:
        try:
            text = content.decode("latin-1").strip()
        except UnicodeDecodeError:
            return None

    # Check for JSON
    if _is_json(text):
        return "json"

    # Check for CSV (has multiple lines with consistent delimiters)
    if _is_csv(text):
        return "csv"

    return None


def _detect_by_extension(filename: str) -> str | None:
    """Detect file type by file extension.

    Args:
        filename: The filename to check.

    Returns:
        The file type based on extension or None.
    """
    ext = Path(filename).suffix.lower()
    extension_map = {
        ".json": "json",
        ".csv": "csv",
        ".xlsx": "xlsx",
        ".xls": "xls",
    }
    return extension_map.get(ext)


def _is_json(text: str) -> bool:
    """Check if text is valid JSON.

    Args:
        text: The text to check.

    Returns:
        True if valid JSON, False otherwise.
    """
    if not text:
        return False

    # JSON should start with [ or {
    if text[0] not in "[{":
        return False

    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


def _is_csv(text: str) -> bool:
    """Check if text appears to be CSV.

    Args:
        text: The text to check.

    Returns:
        True if appears to be CSV, False otherwise.
    """
    if not text:
        return False

    lines = text.split("\n")
    if len(lines) < 2:
        return False

    # Check for common delimiters
    delimiters = [",", ";", "\t"]
    for delimiter in delimiters:
        if delimiter in lines[0]:
            # Check if delimiter count is consistent across first few lines
            first_count = lines[0].count(delimiter)
            if first_count > 0:
                consistent = all(
                    line.count(delimiter) == first_count
                    for line in lines[1:4]
                    if line.strip()
                )
                if consistent:
                    return True

    return False
