"""Tests for JSON to CSV converter."""

import csv
import io

import pytest

from backend.converters.json_to_csv import JsonToCsvConverter


class TestJsonToCsvConverter:
    """Tests for JsonToCsvConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = JsonToCsvConverter()

    def test_convert_simple_json(self, simple_json: bytes):
        """Test converting simple JSON array to CSV."""
        result = self.converter.convert(simple_json)
        assert isinstance(result, bytes)

        # Parse CSV and verify
        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        assert len(rows) == 3
        assert rows[0]["name"] == "Alice"
        assert rows[0]["age"] == "30"
        assert rows[0]["city"] == "New York"

    def test_convert_nested_json(self, nested_json: bytes):
        """Test converting nested JSON with flattening."""
        result = self.converter.convert(nested_json)
        assert isinstance(result, bytes)

        # Parse CSV and verify flattened columns
        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        assert len(rows) == 2
        assert "address.street" in reader.fieldnames
        assert "address.city" in reader.fieldnames
        assert rows[0]["address.street"] == "123 Main St"

    def test_preview_simple_json(self, simple_json: bytes):
        """Test preview generation."""
        result = self.converter.preview(simple_json, rows=2)

        assert "columns" in result
        assert "rows" in result
        assert "total_rows" in result

        assert result["columns"] == ["name", "age", "city"]
        assert len(result["rows"]) == 2
        assert result["total_rows"] == 3

    def test_convert_empty_array_raises(self):
        """Test that empty array raises ValueError."""
        empty_json = b"[]"
        with pytest.raises(ValueError, match="empty"):
            self.converter.convert(empty_json)

    def test_convert_invalid_json_raises(self):
        """Test that invalid JSON raises ValueError."""
        invalid_json = b"not json"
        with pytest.raises(ValueError, match="Invalid JSON"):
            self.converter.convert(invalid_json)

    def test_convert_single_object(self):
        """Test converting a single JSON object."""
        single_obj = b'{"name": "Alice", "age": 30}'
        result = self.converter.convert(single_obj)

        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"
