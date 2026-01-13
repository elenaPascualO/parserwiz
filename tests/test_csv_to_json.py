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
        """Test preview generation with pagination."""
        result = self.converter.preview(simple_csv, page=1, page_size=2)

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

    def test_preview_preserves_leading_zeros(self):
        """Test that preview preserves leading zeros (e.g., '007' stays '007')."""
        csv_with_zeros = b"code,name\n007,James Bond\n001,Agent One\n099,Agent Ninety-Nine"
        result = self.converter.preview(csv_with_zeros, page=1, page_size=10)

        # The preview should preserve "007" as a string, not convert to 7
        assert result["rows"][0][0] == "007"
        assert result["rows"][1][0] == "001"
        assert result["rows"][2][0] == "099"
