"""Tests for JSON to Excel converter."""

import io

import pandas as pd
import pytest

from backend.converters.json_to_excel import JsonToExcelConverter


class TestJsonToExcelConverter:
    """Tests for JsonToExcelConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = JsonToExcelConverter()

    def test_convert_simple_json(self, simple_json: bytes):
        """Test converting simple JSON array to Excel."""
        result = self.converter.convert(simple_json)
        assert isinstance(result, bytes)

        # Parse Excel and verify
        df = pd.read_excel(io.BytesIO(result), engine="openpyxl")

        assert len(df) == 3
        assert list(df.columns) == ["name", "age", "city"]
        assert df.iloc[0]["name"] == "Alice"
        assert df.iloc[0]["age"] == 30

    def test_convert_nested_json(self, nested_json: bytes):
        """Test converting nested JSON with flattening."""
        result = self.converter.convert(nested_json)

        df = pd.read_excel(io.BytesIO(result), engine="openpyxl")

        assert len(df) == 2
        assert "address.street" in df.columns
        assert "address.city" in df.columns

    def test_preview_simple_json(self, simple_json: bytes):
        """Test preview generation."""
        result = self.converter.preview(simple_json, rows=2)

        assert "columns" in result
        assert "rows" in result
        assert "total_rows" in result
        assert len(result["rows"]) == 2

    def test_excel_has_data_sheet(self, simple_json: bytes):
        """Test that Excel file has sheet named 'Data'."""
        result = self.converter.convert(simple_json)

        xlsx = pd.ExcelFile(io.BytesIO(result), engine="openpyxl")
        assert "Data" in xlsx.sheet_names

    def test_convert_empty_array_raises(self):
        """Test that empty array raises ValueError."""
        empty_json = b"[]"
        with pytest.raises(ValueError, match="empty"):
            self.converter.convert(empty_json)
