"""Tests for API endpoints."""

import json

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_preview_json(client: AsyncClient, simple_json: bytes):
    """Test preview endpoint with JSON file."""
    files = {"file": ("test.json", simple_json, "application/json")}
    response = await client.post("/api/preview", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["detected_type"] == "json"
    assert data["columns"] == ["name", "age", "city"]
    assert len(data["rows"]) <= 10
    assert data["total_rows"] == 3


@pytest.mark.asyncio
async def test_preview_csv(client: AsyncClient, simple_csv: bytes):
    """Test preview endpoint with CSV file."""
    files = {"file": ("test.csv", simple_csv, "text/csv")}
    response = await client.post("/api/preview", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["detected_type"] == "csv"
    assert data["columns"] == ["name", "age", "city"]


@pytest.mark.asyncio
async def test_preview_xlsx(client: AsyncClient, simple_xlsx: bytes):
    """Test preview endpoint with XLSX file."""
    files = {
        "file": (
            "test.xlsx",
            simple_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    response = await client.post("/api/preview", files=files)

    assert response.status_code == 200
    data = response.json()

    assert data["detected_type"] == "xlsx"


@pytest.mark.asyncio
async def test_convert_json_to_csv(client: AsyncClient, simple_json: bytes):
    """Test converting JSON to CSV."""
    files = {"file": ("test.json", simple_json, "application/json")}
    data = {"output_format": "csv"}
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert 'filename="test.csv"' in response.headers["content-disposition"]

    # Verify CSV content
    content = response.content.decode("utf-8")
    assert "name,age,city" in content
    assert "Alice" in content


@pytest.mark.asyncio
async def test_convert_json_to_xlsx(client: AsyncClient, simple_json: bytes):
    """Test converting JSON to Excel."""
    files = {"file": ("test.json", simple_json, "application/json")}
    data = {"output_format": "xlsx"}
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]
    assert 'filename="test.xlsx"' in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_convert_csv_to_json(client: AsyncClient, simple_csv: bytes):
    """Test converting CSV to JSON."""
    files = {"file": ("test.csv", simple_csv, "text/csv")}
    data = {"output_format": "json"}
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]

    # Verify JSON content
    result = json.loads(response.content)
    assert isinstance(result, list)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_convert_xlsx_to_json(client: AsyncClient, simple_xlsx: bytes):
    """Test converting Excel to JSON."""
    files = {
        "file": (
            "test.xlsx",
            simple_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    data = {"output_format": "json"}
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 200
    result = json.loads(response.content)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_convert_invalid_format(client: AsyncClient, simple_json: bytes):
    """Test error for invalid conversion format."""
    files = {"file": ("test.json", simple_json, "application/json")}
    data = {"output_format": "pdf"}  # Not supported
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 400
    assert "Cannot convert" in response.json()["detail"]


@pytest.mark.asyncio
async def test_preview_invalid_file(client: AsyncClient):
    """Test error for unsupported file type."""
    files = {"file": ("test.txt", b"plain text", "text/plain")}
    response = await client.post("/api/preview", files=files)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_preview_empty_file(client: AsyncClient):
    """Test error for empty file."""
    files = {"file": ("test.json", b"", "application/json")}
    response = await client.post("/api/preview", files=files)

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()
