"""Tests for CSV to Excel converter."""

import io

import pandas as pd
import pytest

from backend.converters.csv_to_excel import CsvToExcelConverter


class TestCsvToExcelConverter:
    """Tests for CsvToExcelConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = CsvToExcelConverter()

    def test_convert_simple_csv(self, simple_csv: bytes):
        """Test converting simple CSV to Excel."""
        result = self.converter.convert(simple_csv)
        assert isinstance(result, bytes)

        # Parse Excel and verify
        df = pd.read_excel(io.BytesIO(result), engine="openpyxl")

        assert len(df) == 3
        assert list(df.columns) == ["name", "age", "city"]
        assert df.iloc[0]["name"] == "Alice"
        assert df.iloc[0]["age"] == 30
        assert df.iloc[0]["city"] == "New York"

    def test_excel_has_data_sheet(self, simple_csv: bytes):
        """Test that Excel file has sheet named 'Data'."""
        result = self.converter.convert(simple_csv)

        xlsx = pd.ExcelFile(io.BytesIO(result), engine="openpyxl")
        assert "Data" in xlsx.sheet_names

    def test_convert_semicolon_delimiter(self):
        """Test converting CSV with semicolon delimiter."""
        semicolon_csv = b"name;age;city\nAlice;30;New York\nBob;25;Los Angeles"
        result = self.converter.convert(semicolon_csv)

        df = pd.read_excel(io.BytesIO(result), engine="openpyxl")
        assert df.iloc[0]["name"] == "Alice"
        assert df.iloc[1]["name"] == "Bob"

    def test_convert_empty_csv_raises(self):
        """Test that empty CSV raises ValueError."""
        empty_csv = b""
        with pytest.raises(ValueError):
            self.converter.convert(empty_csv)

    def test_handles_missing_values(self):
        """Test handling of missing values in CSV."""
        csv_with_missing = b"name,age,city\nAlice,30,\nBob,,Los Angeles"
        result = self.converter.convert(csv_with_missing)

        df = pd.read_excel(io.BytesIO(result), engine="openpyxl")
        assert pd.isna(df.iloc[0]["city"])
        assert pd.isna(df.iloc[1]["age"])
