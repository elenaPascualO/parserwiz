"""Tests for Excel to CSV converter."""

import csv
import io

import pytest

from backend.converters.excel_to_csv import ExcelToCsvConverter


class TestExcelToCsvConverter:
    """Tests for ExcelToCsvConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = ExcelToCsvConverter()

    def test_convert_simple_xlsx(self, simple_xlsx: bytes):
        """Test converting simple XLSX to CSV."""
        result = self.converter.convert(simple_xlsx)
        assert isinstance(result, bytes)

        # Parse CSV and verify
        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        assert len(rows) == 3
        assert rows[0]["name"] == "Alice"
        assert rows[0]["age"] == "30"
        assert rows[0]["city"] == "New York"

    def test_convert_preserves_all_columns(self, simple_xlsx: bytes):
        """Test that all columns are preserved."""
        result = self.converter.convert(simple_xlsx)

        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        assert reader.fieldnames == ["name", "age", "city"]

    def test_convert_invalid_excel_raises(self):
        """Test that invalid Excel content raises ValueError."""
        invalid_content = b"not an excel file"
        with pytest.raises(ValueError, match="Invalid Excel file|corrupted"):
            self.converter.convert(invalid_content)

    def test_convert_handles_missing_values(self):
        """Test handling of missing values in Excel."""
        import pandas as pd

        # Create Excel file with missing values
        df = pd.DataFrame(
            {"name": ["Alice", "Bob"], "age": [30, None], "city": [None, "Los Angeles"]}
        )
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        excel_content = output.getvalue()

        result = self.converter.convert(excel_content)
        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        assert rows[0]["city"] == ""
        assert rows[1]["age"] == ""
