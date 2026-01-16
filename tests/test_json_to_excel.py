"""Tests for JSON to Excel converter."""

import io
import json

import pandas as pd
import pytest

from backend.converters.json_to_csv import ExportMode
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
        """Test preview generation with pagination."""
        result = self.converter.preview(simple_json, page=1, page_size=2)

        assert "columns" in result
        assert "rows" in result
        assert "total_rows" in result
        assert "current_page" in result
        assert "total_pages" in result
        assert "page_size" in result
        assert len(result["rows"]) == 2
        assert result["current_page"] == 1
        assert result["total_pages"] == 2

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


class TestMultiTableExcel:
    """Tests for MULTI_TABLE export mode with Excel."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = JsonToExcelConverter()

    def test_convert_multi_table_creates_sheets(self, nested2_json: bytes):
        """Test MULTI_TABLE Excel has multiple sheets.

        Expected sheets (top-level arrays only): main, topping
        Note: batters.batter is nested, so becomes JSON string in main sheet.
        """
        result = self.converter.convert(nested2_json, export_mode=ExportMode.MULTI_TABLE)

        xlsx = pd.ExcelFile(io.BytesIO(result), engine="openpyxl")

        # Verify sheets exist (only top-level arrays become separate sheets)
        assert "main" in xlsx.sheet_names
        assert "topping" in xlsx.sheet_names
        assert len(xlsx.sheet_names) == 2

    def test_convert_multi_table_nested3_sheet_contents(self, nested3_json: bytes):
        """Test each sheet has correct row counts and columns."""
        result = self.converter.convert(nested3_json, export_mode=ExportMode.MULTI_TABLE)

        xlsx = pd.ExcelFile(io.BytesIO(result), engine="openpyxl")

        # Only 2 sheets (main + topping)
        assert len(xlsx.sheet_names) == 2

        # Check main sheet
        main_df = pd.read_excel(xlsx, sheet_name="main", dtype=str)
        assert len(main_df) == 3
        assert "_record_id" in main_df.columns
        assert set(main_df["id"]) == {"0001", "0002", "0003"}

        # Check topping sheet (top-level array)
        topping_df = pd.read_excel(xlsx, sheet_name="topping")
        assert len(topping_df) == 16  # 7 + 5 + 4
        assert "_record_id" in topping_df.columns

    def test_convert_multi_table_sheet_name_truncation(self):
        """Test that long table names are truncated to 31 chars for Excel.

        Excel has a 31 character limit for sheet names.
        """
        # Create JSON with a very long array key name
        long_key = "very_long_array_name_that_exceeds_thirty_one_characters"
        data = {
            "id": 1,
            long_key: [{"sub_id": 1}, {"sub_id": 2}],
        }
        content = json.dumps(data).encode("utf-8")

        result = self.converter.convert(content, export_mode=ExportMode.MULTI_TABLE)

        xlsx = pd.ExcelFile(io.BytesIO(result), engine="openpyxl")

        # The long name should be truncated to 31 chars
        truncated_name = long_key[:31]
        assert truncated_name in xlsx.sheet_names
        # Verify the original long name is NOT a sheet name
        assert long_key not in xlsx.sheet_names


class TestSingleRowExcel:
    """Tests for SINGLE_ROW export mode with Excel."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = JsonToExcelConverter()

    def test_convert_single_row_excel_structure(self, nested2_json: bytes):
        """Test SINGLE_ROW Excel has single Data sheet with arrays as text."""
        result = self.converter.convert(nested2_json, export_mode=ExportMode.SINGLE_ROW)

        xlsx = pd.ExcelFile(io.BytesIO(result), engine="openpyxl")

        # Should have only one sheet named "Data"
        assert xlsx.sheet_names == ["Data"]

        # Read the data with dtype=str to preserve original values
        df = pd.read_excel(xlsx, sheet_name="Data", dtype=str)

        # Should have 1 row (no expansion)
        assert len(df) == 1

        # Should have scalar fields
        assert df.iloc[0]["id"] == "0001"
        assert df.iloc[0]["name"] == "Cake"

        # Arrays should be JSON strings
        assert "batters.batter" in df.columns
        assert "topping" in df.columns

        # Verify arrays are parseable JSON strings
        batters_str = df.iloc[0]["batters.batter"]
        batters = json.loads(batters_str)
        assert len(batters) == 4

        topping_str = df.iloc[0]["topping"]
        toppings = json.loads(topping_str)
        assert len(toppings) == 7
