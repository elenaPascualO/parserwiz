"""FastAPI application for DataToolkit."""

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from backend.config import ALLOWED_CONVERSIONS, CORS_ORIGINS, MIME_TYPES, PREVIEW_ROWS
from backend.converters import (
    CsvToJsonConverter,
    ExcelToJsonConverter,
    JsonToCsvConverter,
    JsonToExcelConverter,
)
from backend.utils.file_detection import detect_file_type
from backend.utils.validators import validate_file

app = FastAPI(
    title="DataToolkit",
    description="Web tool for conversion of tabular data (JSON, CSV, Excel)",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Converter registry
CONVERTERS = {
    ("json", "csv"): JsonToCsvConverter(),
    ("json", "xlsx"): JsonToExcelConverter(),
    ("csv", "json"): CsvToJsonConverter(),
    ("xlsx", "json"): ExcelToJsonConverter(),
    ("xls", "json"): ExcelToJsonConverter(),
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
async def preview_file(file: UploadFile = File(...)) -> dict:
    """Preview file data.

    Args:
        file: The uploaded file.

    Returns:
        Preview data with columns, rows, total_rows, and detected_type.

    Raises:
        HTTPException: If file is invalid or cannot be previewed.
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

    # Get preview converter
    converter = PREVIEW_CONVERTERS.get(file_type)
    if not converter:
        raise HTTPException(
            status_code=400, detail=f"Preview not supported for {file_type} files"
        )

    try:
        preview_data = converter.preview(content, rows=PREVIEW_ROWS)
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

    # Generate output filename
    base_name = Path(filename).stem
    output_filename = f"{base_name}.{output_format}"

    # Get MIME type
    mime_type = MIME_TYPES.get(output_format, "application/octet-stream")

    return Response(
        content=converted_content,
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{output_filename}"'},
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
