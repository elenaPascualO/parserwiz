"""Tests for Excel to JSON converter."""

import json

import pytest

from backend.converters.excel_to_json import ExcelToJsonConverter


class TestExcelToJsonConverter:
    """Tests for ExcelToJsonConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = ExcelToJsonConverter()

    def test_convert_simple_xlsx(self, simple_xlsx: bytes):
        """Test converting simple XLSX to JSON."""
        result = self.converter.convert(simple_xlsx)
        assert isinstance(result, bytes)

        data = json.loads(result.decode("utf-8"))

        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == 30
        assert data[0]["city"] == "New York"

    def test_preview_simple_xlsx(self, simple_xlsx: bytes):
        """Test preview generation with pagination."""
        result = self.converter.preview(simple_xlsx, page=1, page_size=2)

        assert "columns" in result
        assert "rows" in result
        assert "total_rows" in result
        assert "current_page" in result
        assert "total_pages" in result
        assert "page_size" in result

        assert result["columns"] == ["name", "age", "city"]
        assert len(result["rows"]) == 2
        assert result["total_rows"] == 3
        assert result["current_page"] == 1
        assert result["total_pages"] == 2
        assert result["page_size"] == 2

    def test_convert_invalid_excel_raises(self):
        """Test that invalid Excel content raises ValueError."""
        invalid_content = b"not an excel file"
        with pytest.raises(ValueError, match="Invalid Excel file|corrupted"):
            self.converter.convert(invalid_content)

    def test_preview_preserves_leading_zeros(self):
        """Test that preview preserves leading zeros in Excel files."""
        import io as std_io

        import pandas as pd

        # Create Excel file with leading zeros stored as text
        df = pd.DataFrame({"code": ["007", "001", "099"], "name": ["James", "Agent", "Nine"]})
        output = std_io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        excel_content = output.getvalue()

        result = self.converter.preview(excel_content, page=1, page_size=10)

        # The preview should preserve values as strings
        assert result["rows"][0][0] == "007"
        assert result["rows"][1][0] == "001"
        assert result["rows"][2][0] == "099"
