"""Security utilities for ParserWiz."""

import os
import re
import urllib.parse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for use in Content-Disposition header.

    Prevents header injection attacks by removing/replacing dangerous characters.

    Args:
        filename: The original filename.

    Returns:
        A sanitized filename safe for HTTP headers.
    """
    if not filename:
        return "download"

    # Remove path components (prevent path traversal)
    filename = os.path.basename(filename)

    # Remove null bytes
    filename = filename.replace("\x00", "")

    # Replace characters that could enable header injection
    # \r\n could inject new headers, " could break the quoted string
    dangerous_chars = {
        "\r": "_",
        "\n": "_",
        '"': "'",
        "\\": "_",
        "/": "_",
    }
    for char, replacement in dangerous_chars.items():
        filename = filename.replace(char, replacement)

    # Remove any remaining control characters (ASCII 0-31)
    filename = re.sub(r"[\x00-\x1f]", "", filename)

    # Limit length to 255 characters (common filesystem limit)
    if len(filename) > 255:
        # Preserve extension
        name, ext = os.path.splitext(filename)
        max_name_len = 255 - len(ext)
        filename = name[:max_name_len] + ext

    # Fallback if filename is empty after sanitization
    if not filename or filename.isspace():
        return "download"

    return filename


def encode_filename_header(filename: str) -> str:
    """Encode filename for Content-Disposition header.

    Uses RFC 5987 encoding for non-ASCII characters.

    Args:
        filename: The sanitized filename.

    Returns:
        A properly formatted Content-Disposition header value.
    """
    filename = sanitize_filename(filename)

    # Check if filename is ASCII-only
    try:
        filename.encode("ascii")
        # ASCII-only: use simple quoted string
        return f'attachment; filename="{filename}"'
    except UnicodeEncodeError:
        # Non-ASCII: use RFC 5987 encoding
        encoded = urllib.parse.quote(filename, safe="")
        return f"attachment; filename*=UTF-8''{encoded}"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers to the response.

        Args:
            request: The incoming request.
            call_next: The next middleware/handler.

        Returns:
            Response with security headers added.
        """
        response = await call_next(request)

        # Basic security headers for all responses
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        # Add CSP for HTML responses
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' https://cloud.umami.is; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self' https://cloud.umami.is; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )

        return response