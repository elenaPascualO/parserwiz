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
        """Test preview generation."""
        result = self.converter.preview(simple_xlsx, rows=2)

        assert "columns" in result
        assert "rows" in result
        assert "total_rows" in result

        assert result["columns"] == ["name", "age", "city"]
        assert len(result["rows"]) == 2
        assert result["total_rows"] == 3

    def test_convert_invalid_excel_raises(self):
        """Test that invalid Excel content raises ValueError."""
        invalid_content = b"not an excel file"
        with pytest.raises(ValueError, match="Could not read"):
            self.converter.convert(invalid_content)
