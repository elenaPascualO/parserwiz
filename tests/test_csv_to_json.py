"""Tests for CSV to JSON converter."""

import json

import pytest

from backend.converters.csv_to_json import CsvToJsonConverter


class TestCsvToJsonConverter:
    """Tests for CsvToJsonConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = CsvToJsonConverter()

    def test_convert_simple_csv(self, simple_csv: bytes):
        """Test converting simple CSV to JSON."""
        result = self.converter.convert(simple_csv)
        assert isinstance(result, bytes)

        data = json.loads(result.decode("utf-8"))

        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == 30
        assert data[0]["city"] == "New York"

    def test_preview_simple_csv(self, simple_csv: bytes):
        """Test preview generation."""
        result = self.converter.preview(simple_csv, rows=2)

        assert "columns" in result
        assert "rows" in result
        assert "total_rows" in result

        assert result["columns"] == ["name", "age", "city"]
        assert len(result["rows"]) == 2
        assert result["total_rows"] == 3

    def test_detect_semicolon_delimiter(self):
        """Test auto-detection of semicolon delimiter."""
        semicolon_csv = b"name;age;city\nAlice;30;New York"
        result = self.converter.convert(semicolon_csv)
        data = json.loads(result.decode("utf-8"))

        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == 30

    def test_detect_tab_delimiter(self):
        """Test auto-detection of tab delimiter."""
        tab_csv = b"name\tage\tcity\nAlice\t30\tNew York"
        result = self.converter.convert(tab_csv)
        data = json.loads(result.decode("utf-8"))

        assert data[0]["name"] == "Alice"

    def test_convert_empty_csv_raises(self):
        """Test that empty CSV raises ValueError."""
        empty_csv = b""
        with pytest.raises(ValueError):
            self.converter.convert(empty_csv)

    def test_handles_missing_values(self):
        """Test handling of missing values in CSV."""
        csv_with_missing = b"name,age,city\nAlice,30,\nBob,,Los Angeles"
        result = self.converter.convert(csv_with_missing)
        data = json.loads(result.decode("utf-8"))

        assert data[0]["city"] is None
        assert data[1]["age"] is None
