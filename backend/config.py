"""Configuration settings for ParserWiz."""

import os

# Environment detection
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION: bool = ENVIRONMENT == "production"

# MIME types for file responses
MIME_TYPES: dict[str, str] = {
    "json": "application/json",
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
}

# Allowed input file extensions
ALLOWED_EXTENSIONS: set[str] = {".json", ".csv", ".xlsx", ".xls"}

# Allowed output formats per input type
ALLOWED_CONVERSIONS: dict[str, list[str]] = {
    "json": ["csv", "xlsx"],
    "csv": ["json", "xlsx"],
    "xlsx": ["json", "csv"],
    "xls": ["json", "csv"],
}

# Max file size in bytes (configurable via environment)
MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024

# Preview settings
PREVIEW_ROWS: int = 500

# JSON expansion settings
# Maximum rows that can be generated when expanding nested arrays (Cartesian product)
MAX_EXPANDED_ROWS: int = 10000
# Threshold for considering JSON "complex" (prompts user for export mode choice)
COMPLEX_JSON_THRESHOLD: int = 100


def get_cors_origins() -> list[str]:
    """Get CORS origins based on environment.

    In production, reads from ALLOWED_ORIGINS environment variable.
    In development, allows common localhost origins.

    Returns:
        List of allowed CORS origins.
    """
    if IS_PRODUCTION:
        # Production: read from environment variable
        origins_str = os.getenv("ALLOWED_ORIGINS", "")
        if origins_str:
            return [
                origin.strip() for origin in origins_str.split(",") if origin.strip()
            ]
        # Fallback: no CORS (same-origin only)
        return []

    # Development: allow common localhost origins
    return [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:63342",  # JetBrains IDE
        "http://127.0.0.1:63342",
        "http://localhost:5500",  # VS Code Live Server
        "http://127.0.0.1:5500",
    ]


# CORS settings (computed based on environment)
CORS_ORIGINS: list[str] = get_cors_origins()


# Discord webhook for feedback (optional)
DISCORD_WEBHOOK_URL: str | None = os.getenv("DISCORD_WEBHOOK_URL")
