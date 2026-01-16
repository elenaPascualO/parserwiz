"""Tests for JSON to CSV converter."""

import csv
import io
import json

import pytest

from backend.converters.json_to_csv import ExportMode, JsonToCsvConverter


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
        """Test preview generation with pagination."""
        result = self.converter.preview(simple_json, page=1, page_size=2)

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

    def test_convert_empty_array_raises(self):
        """Test that empty array raises ValueError."""
        empty_json = b"[]"
        with pytest.raises(ValueError, match="empty"):
            self.converter.convert(empty_json)

    def test_convert_invalid_json_raises(self):
        """Test that invalid JSON raises ValueError with line/column info."""
        invalid_json = b"not json"
        with pytest.raises(ValueError, match=r"Invalid JSON at line \d+, column \d+"):
            self.converter.convert(invalid_json)

    def test_convert_invalid_json_shows_position(self):
        """Test that JSON error shows exact position of error."""
        # JSON with error on line 3
        invalid_json = b'[\n  {"name": "Alice"},\n  {"name": }\n]'
        with pytest.raises(ValueError, match=r"line 3"):
            self.converter.convert(invalid_json)

    def test_convert_single_object(self):
        """Test converting a single JSON object."""
        single_obj = b'{"name": "Alice", "age": 30}'
        result = self.converter.convert(single_obj)

        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"

    def test_convert_nested2_single_object_with_arrays(self):
        """Test nested2.json: single object with multiple nested arrays.

        The object has 4 batters and 7 toppings, which should expand to
        4 × 7 = 28 rows via Cartesian product.
        """
        with open("tests/sample_files/nested2.json", "rb") as f:
            content = f.read()

        result = self.converter.convert(content)
        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        # 4 batters × 7 toppings = 28 rows
        assert len(rows) == 28

        # Verify scalar fields are preserved in every row
        for row in rows:
            assert row["id"] == "0001"
            assert row["type"] == "donut"
            assert row["name"] == "Cake"
            assert row["ppu"] == "0.55"

        # Verify nested array fields are expanded
        assert "batters.batter.id" in reader.fieldnames
        assert "batters.batter.type" in reader.fieldnames
        assert "topping.id" in reader.fieldnames
        assert "topping.type" in reader.fieldnames

        # Verify first row has correct batter and topping
        assert rows[0]["batters.batter.id"] == "1001"
        assert rows[0]["batters.batter.type"] == "Regular"
        assert rows[0]["topping.id"] == "5001"
        assert rows[0]["topping.type"] == "None"

    def test_convert_nested3_array_with_nested_arrays(self):
        """Test nested3.json: array of objects each with nested arrays.

        - Object 1: 4 batters × 7 toppings = 28 rows
        - Object 2: 1 batter × 5 toppings = 5 rows
        - Object 3: 2 batters × 4 toppings = 8 rows
        - Total: 41 rows
        """
        with open("tests/sample_files/nested3.json", "rb") as f:
            content = f.read()

        result = self.converter.convert(content)
        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        # Total expected rows: 28 + 5 + 8 = 41
        assert len(rows) == 41

        # Check that all 3 products are represented
        product_ids = set(row["id"] for row in rows)
        assert product_ids == {"0001", "0002", "0003"}

        # Count rows per product
        rows_per_product = {}
        for row in rows:
            pid = row["id"]
            rows_per_product[pid] = rows_per_product.get(pid, 0) + 1

        assert rows_per_product["0001"] == 28  # 4 × 7
        assert rows_per_product["0002"] == 5   # 1 × 5
        assert rows_per_product["0003"] == 8   # 2 × 4

    def test_expansion_limit_exceeded(self):
        """Test that exceeding MAX_EXPANDED_ROWS raises ValueError."""
        # Create JSON with arrays that would produce too many rows
        # Using a structure with many nested arrays
        import json
        from backend.config import MAX_EXPANDED_ROWS

        # Create arrays that will exceed the limit when multiplied
        # e.g., 200 items × 200 items = 40000 rows > 10000 limit
        large_array = [{"id": str(i)} for i in range(200)]
        data = {
            "name": "test",
            "array1": large_array,
            "array2": large_array,
        }

        content = json.dumps(data).encode("utf-8")

        with pytest.raises(ValueError, match=f"limit: {MAX_EXPANDED_ROWS}"):
            self.converter.convert(content)

    def test_preview_nested2_pagination(self):
        """Test pagination works correctly with expanded nested data."""
        with open("tests/sample_files/nested2.json", "rb") as f:
            content = f.read()

        # Get first page
        result = self.converter.preview(content, page=1, page_size=10)

        assert result["total_rows"] == 28
        assert result["total_pages"] == 3  # 28 rows / 10 per page = 3 pages
        assert result["current_page"] == 1
        assert len(result["rows"]) == 10

        # Get last page
        result = self.converter.preview(content, page=3, page_size=10)

        assert result["current_page"] == 3
        assert len(result["rows"]) == 8  # 28 - 20 = 8 remaining rows


class TestMultiTableMode:
    """Tests for MULTI_TABLE export mode."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = JsonToCsvConverter()

    def test_convert_multi_table_nested2_structure(self, nested2_json: bytes):
        """Test MULTI_TABLE mode extracts correct tables from nested2.json.

        Expected tables (top-level arrays only):
        - main: 1 row with scalar fields + nested objects flattened
        - topping: 7 rows (_record_id, id, type)

        Note: batters.batter is a nested array (inside batters object),
        so it becomes a JSON string in the main table, not a separate table.
        """
        tables = self.converter.convert_multi_table(nested2_json)

        # Verify tables exist (only top-level arrays become separate tables)
        assert "main" in tables
        assert "topping" in tables
        assert len(tables) == 2

        # Verify main table
        main_df = tables["main"]
        assert len(main_df) == 1
        assert "_record_id" in main_df.columns
        assert "id" in main_df.columns
        assert "name" in main_df.columns
        assert "ppu" in main_df.columns
        assert main_df.iloc[0]["id"] == "0001"
        assert main_df.iloc[0]["name"] == "Cake"

        # Verify nested array (batters.batter) is a JSON string in main
        assert "batters.batter" in main_df.columns
        batters_str = main_df.iloc[0]["batters.batter"]
        batters = json.loads(batters_str)
        assert len(batters) == 4  # 4 batter items as JSON

        # Verify topping table (top-level array)
        topping_df = tables["topping"]
        assert len(topping_df) == 7
        assert "_record_id" in topping_df.columns
        assert all(topping_df["_record_id"] == 1)

    def test_convert_multi_table_nested3_structure(self, nested3_json: bytes):
        """Test MULTI_TABLE mode with array of objects (nested3.json).

        Expected (top-level arrays only):
        - main: 3 rows (one per product with _record_id 1, 2, 3)
        - topping: 16 rows total (7+5+4 across products)

        Note: batters.batter is nested, so becomes JSON string in main table.
        """
        tables = self.converter.convert_multi_table(nested3_json)

        # Verify tables (only top-level array becomes separate table)
        assert "main" in tables
        assert "topping" in tables
        assert len(tables) == 2

        # Verify main table
        main_df = tables["main"]
        assert len(main_df) == 3
        assert list(main_df["_record_id"]) == [1, 2, 3]
        assert set(main_df["id"]) == {"0001", "0002", "0003"}

        # Verify nested array (batters.batter) is JSON string in main
        assert "batters.batter" in main_df.columns
        # First product has 4 batters
        batters1 = json.loads(main_df.iloc[0]["batters.batter"])
        assert len(batters1) == 4
        # Second product has 1 batter
        batters2 = json.loads(main_df.iloc[1]["batters.batter"])
        assert len(batters2) == 1
        # Third product has 2 batters
        batters3 = json.loads(main_df.iloc[2]["batters.batter"])
        assert len(batters3) == 2

        # Verify topping table (top-level array)
        topping_df = tables["topping"]
        assert len(topping_df) == 16  # 7 + 5 + 4

    def test_convert_multi_table_csv_raises(self, nested2_json: bytes):
        """Test that CSV convert() with MULTI_TABLE mode raises ValueError."""
        with pytest.raises(ValueError, match="MULTI_TABLE.*ZIP"):
            self.converter.convert(nested2_json, export_mode=ExportMode.MULTI_TABLE)

    def test_preview_multi_table_returns_table_info(self, nested2_json: bytes):
        """Test that preview with MULTI_TABLE returns table_info dict with row counts."""
        result = self.converter.preview(
            nested2_json, page=1, page_size=10, export_mode=ExportMode.MULTI_TABLE
        )

        # Should have table_info
        assert "table_info" in result
        assert "preview_table" in result
        assert result["preview_table"] == "main"

        # Check table counts (only top-level arrays become separate tables)
        table_info = result["table_info"]
        assert table_info["main"] == 1
        assert table_info["topping"] == 7
        assert len(table_info) == 2


class TestSingleRowMode:
    """Tests for SINGLE_ROW export mode."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = JsonToCsvConverter()

    def test_convert_single_row_nested2_preserves_arrays(self, nested2_json: bytes):
        """Test SINGLE_ROW mode keeps arrays as JSON strings.

        Expected: 1 row with columns including:
        - id, type, name, ppu (scalar values)
        - batters.batter (JSON string of array)
        - topping (JSON string of array)
        """
        result = self.converter.convert(nested2_json, export_mode=ExportMode.SINGLE_ROW)

        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        # Should be exactly 1 row (no expansion)
        assert len(rows) == 1

        row = rows[0]

        # Verify scalar fields
        assert row["id"] == "0001"
        assert row["name"] == "Cake"
        assert row["ppu"] == "0.55"

        # Verify arrays are JSON strings
        assert "batters.batter" in reader.fieldnames
        assert "topping" in reader.fieldnames

        # Parse the JSON strings to verify content
        batters = json.loads(row["batters.batter"])
        assert len(batters) == 4
        assert batters[0]["type"] == "Regular"

        toppings = json.loads(row["topping"])
        assert len(toppings) == 7
        assert toppings[0]["type"] == "None"

    def test_convert_single_row_nested3_arrays_as_strings(self, nested3_json: bytes):
        """Test SINGLE_ROW mode with array of objects.

        Expected: 3 rows, each with arrays serialized as JSON strings.
        """
        result = self.converter.convert(nested3_json, export_mode=ExportMode.SINGLE_ROW)

        reader = csv.DictReader(io.StringIO(result.decode("utf-8")))
        rows = list(reader)

        # Should be 3 rows (one per root object, no expansion)
        assert len(rows) == 3

        # Check each product has correct data
        product_ids = [row["id"] for row in rows]
        assert product_ids == ["0001", "0002", "0003"]

        # Verify first product arrays are JSON strings
        first_row = rows[0]
        batters = json.loads(first_row["batters.batter"])
        assert len(batters) == 4

        # Verify second product has fewer batters
        second_row = rows[1]
        batters = json.loads(second_row["batters.batter"])
        assert len(batters) == 1

    def test_preview_single_row_mode(self, nested2_json: bytes):
        """Test preview in SINGLE_ROW mode shows correct structure."""
        result = self.converter.preview(
            nested2_json, page=1, page_size=10, export_mode=ExportMode.SINGLE_ROW
        )

        # Should have 1 row (no expansion)
        assert result["total_rows"] == 1
        assert len(result["rows"]) == 1

        # Should have array columns as strings
        columns = result["columns"]
        assert "batters.batter" in columns
        assert "topping" in columns

        # The row values should be JSON strings for arrays
        row = result["rows"][0]
        # Find the index of batters.batter column
        batter_idx = columns.index("batters.batter")
        batter_value = row[batter_idx]
        # Should be parseable as JSON
        parsed = json.loads(batter_value)
        assert len(parsed) == 4
