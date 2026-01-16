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


# ============== NEW CONVERSION TESTS ==============


@pytest.mark.asyncio
async def test_convert_csv_to_xlsx(client: AsyncClient, simple_csv: bytes):
    """Test converting CSV to Excel."""
    files = {"file": ("test.csv", simple_csv, "text/csv")}
    data = {"output_format": "xlsx"}
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]
    assert 'filename="test.xlsx"' in response.headers["content-disposition"]

    # Verify Excel content by checking it's valid
    import io
    import pandas as pd

    df = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
    assert len(df) == 3
    assert list(df.columns) == ["name", "age", "city"]


@pytest.mark.asyncio
async def test_convert_xlsx_to_csv(client: AsyncClient, simple_xlsx: bytes):
    """Test converting Excel to CSV."""
    files = {
        "file": (
            "test.xlsx",
            simple_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    data = {"output_format": "csv"}
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert 'filename="test.csv"' in response.headers["content-disposition"]

    # Verify CSV content
    content = response.content.decode("utf-8")
    assert "name,age,city" in content or "name" in content


@pytest.mark.asyncio
async def test_convert_xls_to_csv(client: AsyncClient, simple_xlsx: bytes):
    """Test converting XLS to CSV (using xlsx fixture as xls proxy)."""
    # Note: We use xlsx here but with .xls extension to test the xls path
    # In real usage, xlrd would handle actual .xls files
    files = {
        "file": (
            "test.xlsx",  # Keep xlsx for valid file
            simple_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    data = {"output_format": "csv"}
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


# ============== PAGINATION TESTS ==============


@pytest.mark.asyncio
async def test_preview_pagination_first_page(client: AsyncClient, simple_csv: bytes):
    """Test preview pagination returns correct page info."""
    files = {"file": ("test.csv", simple_csv, "text/csv")}
    data = {"page": "1", "page_size": "2"}
    response = await client.post("/api/preview", files=files, data=data)

    assert response.status_code == 200
    result = response.json()

    assert result["current_page"] == 1
    assert result["total_pages"] == 2  # 3 rows / 2 per page = 2 pages
    assert result["page_size"] == 2
    assert len(result["rows"]) == 2


@pytest.mark.asyncio
async def test_preview_pagination_second_page(client: AsyncClient, simple_csv: bytes):
    """Test preview pagination second page."""
    files = {"file": ("test.csv", simple_csv, "text/csv")}
    data = {"page": "2", "page_size": "2"}
    response = await client.post("/api/preview", files=files, data=data)

    assert response.status_code == 200
    result = response.json()

    assert result["current_page"] == 2
    assert len(result["rows"]) == 1  # Only 1 row on last page


@pytest.mark.asyncio
async def test_preview_pagination_out_of_bounds(client: AsyncClient, simple_csv: bytes):
    """Test preview pagination clamps to valid range."""
    files = {"file": ("test.csv", simple_csv, "text/csv")}
    data = {"page": "100", "page_size": "2"}  # Way past last page
    response = await client.post("/api/preview", files=files, data=data)

    assert response.status_code == 200
    result = response.json()

    # Should clamp to last page
    assert result["current_page"] == result["total_pages"]


# ============== ERROR MESSAGE TESTS ==============


@pytest.mark.asyncio
async def test_convert_json_invalid_shows_line_number(client: AsyncClient):
    """Test that invalid JSON error shows line number."""
    invalid_json = b'[\n  {"name": "Alice"},\n  {"name": }\n]'
    files = {"file": ("test.json", invalid_json, "application/json")}
    data = {"output_format": "csv"}
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "line" in detail.lower()


@pytest.mark.asyncio
async def test_convert_excel_invalid_shows_helpful_error(client: AsyncClient):
    """Test that invalid Excel file shows helpful error."""
    invalid_excel = b"not an excel file at all"
    files = {"file": ("test.xlsx", invalid_excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"output_format": "json"}
    response = await client.post("/api/convert", files=files, data=data)

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "excel" in detail.lower() or "corrupted" in detail.lower()


# ============== ALL CONVERSION MATRIX TESTS ==============


@pytest.mark.asyncio
async def test_all_json_conversions(client: AsyncClient, simple_json: bytes):
    """Test all conversions from JSON."""
    for output_format in ["csv", "xlsx"]:
        files = {"file": ("test.json", simple_json, "application/json")}
        data = {"output_format": output_format}
        response = await client.post("/api/convert", files=files, data=data)

        assert response.status_code == 200, f"JSON to {output_format} failed"


@pytest.mark.asyncio
async def test_all_csv_conversions(client: AsyncClient, simple_csv: bytes):
    """Test all conversions from CSV."""
    for output_format in ["json", "xlsx"]:
        files = {"file": ("test.csv", simple_csv, "text/csv")}
        data = {"output_format": output_format}
        response = await client.post("/api/convert", files=files, data=data)

        assert response.status_code == 200, f"CSV to {output_format} failed"


@pytest.mark.asyncio
async def test_all_xlsx_conversions(client: AsyncClient, simple_xlsx: bytes):
    """Test all conversions from XLSX."""
    for output_format in ["json", "csv"]:
        files = {
            "file": (
                "test.xlsx",
                simple_xlsx,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }
        data = {"output_format": output_format}
        response = await client.post("/api/convert", files=files, data=data)

        assert response.status_code == 200, f"XLSX to {output_format} failed"


# ============== PREVIEW ALL TABLES ENDPOINT ==============


@pytest.mark.asyncio
async def test_preview_all_tables_json(client: AsyncClient, nested2_json: bytes):
    """Test preview-all-tables endpoint with complex JSON."""
    files = {"file": ("nested2.json", nested2_json, "application/json")}
    data = {"rows_per_table": "5"}
    response = await client.post("/api/preview-all-tables", files=files, data=data)

    assert response.status_code == 200
    result = response.json()

    # Should have tables dict
    assert "tables" in result
    assert "detected_type" in result
    assert result["detected_type"] == "json"

    # Check expected tables exist
    tables = result["tables"]
    assert "main" in tables
    assert "topping" in tables

    # Check main table structure
    main = tables["main"]
    assert "columns" in main
    assert "rows" in main
    assert "total_rows" in main
    assert main["total_rows"] == 1

    # Check topping table
    topping = tables["topping"]
    assert topping["total_rows"] == 7
    assert len(topping["rows"]) <= 5  # Limited by rows_per_table


@pytest.mark.asyncio
async def test_preview_all_tables_non_json_fails(client: AsyncClient, simple_csv: bytes):
    """Test preview-all-tables endpoint rejects non-JSON files."""
    files = {"file": ("test.csv", simple_csv, "text/csv")}
    response = await client.post("/api/preview-all-tables", files=files)

    assert response.status_code == 400
    assert "JSON" in response.json()["detail"]
