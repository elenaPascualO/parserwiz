"""FastAPI application for DataToolkit."""

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from backend.config import ALLOWED_CONVERSIONS, CORS_ORIGINS, MIME_TYPES, PREVIEW_ROWS
from backend.converters import (
    CsvToExcelConverter,
    CsvToJsonConverter,
    ExcelToCsvConverter,
    ExcelToJsonConverter,
    JsonToCsvConverter,
    JsonToExcelConverter,
)
from backend.utils.file_detection import detect_file_type
from backend.utils.security import SecurityHeadersMiddleware, encode_filename_header
from backend.utils.validators import validate_file

app = FastAPI(
    title="DataToolkit",
    description="Web tool for conversion of tabular data (JSON, CSV, Excel)",
    version="0.1.0",
)

# Security headers middleware (should be added first to apply to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # No cookies needed
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# Converter registry
CONVERTERS = {
    ("json", "csv"): JsonToCsvConverter(),
    ("json", "xlsx"): JsonToExcelConverter(),
    ("csv", "json"): CsvToJsonConverter(),
    ("csv", "xlsx"): CsvToExcelConverter(),
    ("xlsx", "json"): ExcelToJsonConverter(),
    ("xlsx", "csv"): ExcelToCsvConverter(),
    ("xls", "json"): ExcelToJsonConverter(),
    ("xls", "csv"): ExcelToCsvConverter(),
}

# Preview converters (one per input type)
PREVIEW_CONVERTERS = {
    "json": JsonToCsvConverter(),
    "csv": CsvToJsonConverter(),
    "xlsx": ExcelToJsonConverter(),
    "xls": ExcelToJsonConverter(),
}


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Status dictionary.
    """
    return {"status": "ok"}


@app.post("/api/preview")
async def preview_file(
    file: UploadFile = File(...),
    page: int = Form(default=1),
    page_size: int = Form(default=PREVIEW_ROWS),
) -> dict:
    """Preview file data with pagination support.

    Args:
        file: The uploaded file.
        page: Page number (1-indexed). Defaults to 1.
        page_size: Number of rows per page. Defaults to PREVIEW_ROWS (10).

    Returns:
        Preview data with columns, rows, total_rows, detected_type,
        current_page, total_pages, and page_size.

    Raises:
        HTTPException: If file is invalid or cannot be previewed.
    """
    content = await file.read()
    filename = file.filename or "unknown"

    # Validate pagination parameters
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = PREVIEW_ROWS
    if page_size > 100:
        page_size = 100  # Cap at 100 rows per page

    # Validate file
    is_valid, error = validate_file(content, filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Detect file type
    file_type = detect_file_type(content, filename)
    if not file_type:
        raise HTTPException(status_code=400, detail="Could not detect file type")

    # Get preview converter
    converter = PREVIEW_CONVERTERS.get(file_type)
    if not converter:
        raise HTTPException(
            status_code=400, detail=f"Preview not supported for {file_type} files"
        )

    try:
        preview_data = converter.preview(content, page=page, page_size=page_size)
        preview_data["detected_type"] = file_type
        return preview_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/convert")
async def convert_file(
    file: UploadFile = File(...),
    output_format: str = Form(...),
) -> Response:
    """Convert file to specified format.

    Args:
        file: The uploaded file.
        output_format: Target format (csv, xlsx, json).

    Returns:
        The converted file.

    Raises:
        HTTPException: If conversion fails or is not supported.
    """
    content = await file.read()
    filename = file.filename or "unknown"

    # Validate file
    is_valid, error = validate_file(content, filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Detect file type
    file_type = detect_file_type(content, filename)
    if not file_type:
        raise HTTPException(status_code=400, detail="Could not detect file type")

    # Normalize output format
    output_format = output_format.lower().strip()

    # Check if conversion is allowed
    allowed_outputs = ALLOWED_CONVERSIONS.get(file_type, [])
    if output_format not in allowed_outputs:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot convert {file_type} to {output_format}. "
            f"Allowed: {', '.join(allowed_outputs)}",
        )

    # Get converter
    converter = CONVERTERS.get((file_type, output_format))
    if not converter:
        raise HTTPException(
            status_code=400,
            detail=f"Converter not available for {file_type} to {output_format}",
        )

    try:
        converted_content = converter.convert(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Generate output filename (sanitized for security)
    base_name = Path(filename).stem
    output_filename = f"{base_name}.{output_format}"

    # Get MIME type
    mime_type = MIME_TYPES.get(output_format, "application/octet-stream")

    # Use secure filename encoding for Content-Disposition header
    content_disposition = encode_filename_header(output_filename)

    return Response(
        content=converted_content,
        media_type=mime_type,
        headers={"Content-Disposition": content_disposition},
    )


# Mount frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/")
async def root():
    """Serve the frontend index.html."""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "DataToolkit API", "docs": "/docs"}
