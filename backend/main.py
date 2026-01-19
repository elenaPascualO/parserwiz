"""FastAPI application for ParserWiz."""

import io
import zipfile
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from backend.config import (
    ALLOWED_CONVERSIONS,
    CORS_ORIGINS,
    DISCORD_WEBHOOK_URL,
    MIME_TYPES,
    PREVIEW_ROWS,
)
from backend.converters import (
    CsvToExcelConverter,
    CsvToJsonConverter,
    ExcelToCsvConverter,
    ExcelToJsonConverter,
    JsonToCsvConverter,
    JsonToExcelConverter,
)
from backend.converters.json_to_csv import ExportMode
from backend.utils.file_detection import detect_file_type
from backend.utils.security import SecurityHeadersMiddleware, encode_filename_header
from backend.utils.validators import validate_file

app = FastAPI(
    title="ParserWiz",
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


@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)) -> dict:
    """Analyze JSON file structure to determine complexity.

    Args:
        file: The uploaded file.

    Returns:
        Analysis results with is_complex, estimated_rows, arrays_found,
        and expansion_formula.

    Raises:
        HTTPException: If file is invalid or not JSON.
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

    # Only JSON files need complexity analysis
    if file_type != "json":
        return {
            "is_complex": False,
            "estimated_rows": None,
            "arrays_found": [],
            "expansion_formula": None,
            "message": "Only JSON files require complexity analysis",
        }

    # Analyze JSON structure
    converter = JsonToCsvConverter()
    try:
        analysis = converter.analyze_json_structure(content)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/preview")
async def preview_file(
    file: UploadFile = File(...),
    page: int = Form(default=1),
    page_size: int = Form(default=PREVIEW_ROWS),
    export_mode: str = Form(default="normal"),
) -> dict:
    """Preview file data with pagination support.

    Args:
        file: The uploaded file.
        page: Page number (1-indexed). Defaults to 1.
        page_size: Number of rows per page. Defaults to PREVIEW_ROWS (10).
        export_mode: Export mode for JSON files (normal, multi_table, single_row).

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
        # For JSON files, use export_mode
        if file_type == "json":
            mode = ExportMode(export_mode)
            preview_data = converter.preview(
                content, page=page, page_size=page_size, export_mode=mode
            )
        else:
            preview_data = converter.preview(content, page=page, page_size=page_size)

        preview_data["detected_type"] = file_type
        return preview_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/preview-all-tables")
async def preview_all_tables(
    file: UploadFile = File(...),
    rows_per_table: int = Form(default=5),
) -> dict:
    """Preview all tables from complex JSON in multi-table mode.

    Returns a preview of all extracted tables, each with limited rows,
    allowing users to see the full multi-table structure before downloading.

    Args:
        file: The uploaded JSON file.
        rows_per_table: Maximum rows per table. Defaults to 5.

    Returns:
        Dictionary with tables info, each containing columns, rows, total_rows.

    Raises:
        HTTPException: If file is invalid or not JSON.
    """
    content = await file.read()
    filename = file.filename or "unknown"

    # Validate file
    is_valid, error = validate_file(content, filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Detect file type
    file_type = detect_file_type(content, filename)
    if file_type != "json":
        raise HTTPException(
            status_code=400,
            detail="Only JSON files are supported for multi-table preview",
        )

    # Validate rows_per_table
    if rows_per_table < 1:
        rows_per_table = 5
    if rows_per_table > 100:
        rows_per_table = 100

    converter = JsonToCsvConverter()
    try:
        result = converter.preview_all_tables(content, rows_per_table)
        result["detected_type"] = "json"
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/convert")
async def convert_file(
    file: UploadFile = File(...),
    output_format: str = Form(...),
    export_mode: str = Form(default="normal"),
) -> Response:
    """Convert file to specified format.

    Args:
        file: The uploaded file.
        output_format: Target format (csv, xlsx, json).
        export_mode: Export mode for JSON files (normal, multi_table, single_row).

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

    # Generate base output filename
    base_name = Path(filename).stem

    try:
        # Handle JSON to CSV/Excel with export_mode
        if file_type == "json":
            mode = ExportMode(export_mode)

            # Multi-table CSV -> ZIP file with multiple CSVs
            if mode == ExportMode.MULTI_TABLE and output_format == "csv":
                tables = converter.convert_multi_table(content)
                zip_content = _create_csv_zip(tables, base_name)
                output_filename = f"{base_name}.zip"
                return Response(
                    content=zip_content,
                    media_type="application/zip",
                    headers={
                        "Content-Disposition": encode_filename_header(output_filename)
                    },
                )

            # Other modes (including multi-table Excel)
            converted_content = converter.convert(content, export_mode=mode)
        else:
            converted_content = converter.convert(content)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Generate output filename
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


def _create_csv_zip(tables: dict, base_name: str) -> bytes:
    """Create a ZIP file containing multiple CSV files.

    Args:
        tables: Dictionary mapping table names to DataFrames.
        base_name: Base name for CSV files.

    Returns:
        ZIP file content as bytes.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for table_name, df in tables.items():
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue().encode("utf-8")

            # Use table name as filename
            csv_filename = f"{base_name}_{table_name}.csv"
            zip_file.writestr(csv_filename, csv_content)

    return zip_buffer.getvalue()


class FeedbackRequest(BaseModel):
    """Request model for feedback submission."""

    email: str = ""
    message: str


@app.post("/api/feedback")
async def send_feedback(feedback: FeedbackRequest) -> dict[str, str]:
    """Send user feedback to Discord webhook.

    Args:
        feedback: The feedback data with optional email and message.

    Returns:
        Status dictionary.

    Raises:
        HTTPException: If feedback cannot be sent.
    """
    if not feedback.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    if not DISCORD_WEBHOOK_URL:
        raise HTTPException(status_code=503, detail="Feedback service not configured")

    payload = {
        "embeds": [
            {
                "title": "New Feedback",
                "fields": [
                    {"name": "From", "value": feedback.email or "Anonymous"},
                    {"name": "Message", "value": feedback.message[:1000]},
                ],
                "color": 5814783,
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10.0)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail="Failed to send feedback") from e

    return {"status": "sent"}


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
    return {"message": "ParserWiz API", "docs": "/docs"}
