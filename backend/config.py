"""Configuration settings for DataToolkit."""

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
    "csv": ["json"],
    "xlsx": ["json"],
    "xls": ["json"],
}

# Max file size in bytes (10MB)
MAX_FILE_SIZE: int = 10 * 1024 * 1024

# Preview settings
PREVIEW_ROWS: int = 10

# CORS settings
CORS_ORIGINS: list[str] = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://localhost:63342",  # JetBrains IDE
    "http://127.0.0.1:63342",
    "http://localhost:5500",   # VS Code Live Server
    "http://127.0.0.1:5500",
]
