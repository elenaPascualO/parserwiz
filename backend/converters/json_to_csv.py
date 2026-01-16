"""JSON to CSV converter."""

import io
import itertools
import json
from enum import Enum
from typing import Any

import pandas as pd

from backend.config import COMPLEX_JSON_THRESHOLD, MAX_EXPANDED_ROWS
from backend.converters.base import BaseConverter


class ExportMode(str, Enum):
    """Export modes for JSON conversion."""

    NORMAL = "normal"  # Current behavior (Cartesian product expansion)
    MULTI_TABLE = "multi_table"  # Multiple tables (sheets/files), one per array
    SINGLE_ROW = "single_row"  # Single row, arrays as JSON strings


class JsonToCsvConverter(BaseConverter):
    """Converts JSON data to CSV format.

    Handles nested JSON structures by expanding arrays into multiple rows
    (Cartesian product / denormalization).
    """

    def analyze_json_structure(self, content: bytes) -> dict[str, Any]:
        """Analyze JSON structure to determine complexity.

        Calculates the potential Cartesian product expansion without
        actually performing the expansion.

        Args:
            content: JSON content as bytes.

        Returns:
            Dictionary with analysis results:
            {
                "is_complex": bool,
                "estimated_rows": int,
                "arrays_found": [{"path": str, "count": int}, ...],
                "expansion_formula": str  # e.g., "3 × 6 × 4 = 72"
            }

        Raises:
            ValueError: If JSON is invalid.
        """
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError(
                f"File encoding error: Unable to decode as UTF-8. Details: {e}"
            ) from e

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}"
            ) from e

        # Analyze structure
        if isinstance(data, list):
            if not data:
                return {
                    "is_complex": False,
                    "estimated_rows": 0,
                    "arrays_found": [],
                    "expansion_formula": "0",
                }
            # For array of objects, analyze the first object as representative
            # and multiply by array length
            if all(isinstance(item, dict) for item in data):
                # Analyze first item structure
                arrays_info = self._find_arrays_in_object(data[0])
                single_obj_rows = self._calculate_expansion_rows(arrays_info)
                total_rows = single_obj_rows * len(data)

                return {
                    "is_complex": total_rows > COMPLEX_JSON_THRESHOLD
                    and len(arrays_info) >= 2,
                    "estimated_rows": total_rows,
                    "arrays_found": arrays_info,
                    "expansion_formula": self._build_formula(arrays_info, len(data)),
                }

            return {
                "is_complex": False,
                "estimated_rows": len(data),
                "arrays_found": [],
                "expansion_formula": str(len(data)),
            }

        elif isinstance(data, dict):
            arrays_info = self._find_arrays_in_object(data)
            estimated_rows = self._calculate_expansion_rows(arrays_info)

            return {
                "is_complex": estimated_rows > COMPLEX_JSON_THRESHOLD
                and len(arrays_info) >= 2,
                "estimated_rows": estimated_rows,
                "arrays_found": arrays_info,
                "expansion_formula": self._build_formula(arrays_info),
            }

        return {
            "is_complex": False,
            "estimated_rows": 1,
            "arrays_found": [],
            "expansion_formula": "1",
        }

    def _find_arrays_in_object(
        self, obj: dict[str, Any], prefix: str = ""
    ) -> list[dict[str, Any]]:
        """Find all arrays of objects in a JSON object.

        Args:
            obj: The object to analyze.
            prefix: Current path prefix.

        Returns:
            List of dicts with path and count for each array found.
        """
        arrays: list[dict[str, Any]] = []

        for key, value in obj.items():
            full_key = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                # Recurse into nested objects
                nested_arrays = self._find_arrays_in_object(value, f"{full_key}.")
                arrays.extend(nested_arrays)

            elif isinstance(value, list):
                if value and all(isinstance(item, dict) for item in value):
                    # Found an array of objects
                    arrays.append({"path": full_key, "count": len(value)})
                    # Also check inside array items for nested arrays
                    if value:
                        nested_in_items = self._find_arrays_in_object(
                            value[0], f"{full_key}."
                        )
                        arrays.extend(nested_in_items)

        return arrays

    def _calculate_expansion_rows(
        self, arrays_info: list[dict[str, Any]]
    ) -> int:
        """Calculate estimated rows from Cartesian product.

        Args:
            arrays_info: List of arrays with their counts.

        Returns:
            Estimated row count.
        """
        if not arrays_info:
            return 1

        result = 1
        for arr in arrays_info:
            result *= arr["count"]
        return result

    def _build_formula(
        self, arrays_info: list[dict[str, Any]], multiplier: int = 1
    ) -> str:
        """Build a human-readable expansion formula.

        Args:
            arrays_info: List of arrays with their counts.
            multiplier: Additional multiplier (e.g., array length for root arrays).

        Returns:
            Formula string like "3 × 6 × 4 = 72"
        """
        if not arrays_info:
            return str(multiplier) if multiplier > 1 else "1"

        counts = [arr["count"] for arr in arrays_info]
        if multiplier > 1:
            counts.insert(0, multiplier)

        if len(counts) == 1:
            return str(counts[0])

        result = 1
        for c in counts:
            result *= c

        formula_parts = " × ".join(str(c) for c in counts)
        return f"{formula_parts} = {result}"

    def convert(
        self, content: bytes, export_mode: ExportMode = ExportMode.NORMAL
    ) -> bytes:
        """Convert JSON to CSV.

        Args:
            content: JSON content as bytes.
            export_mode: Export mode (NORMAL, MULTI_TABLE, or SINGLE_ROW).

        Returns:
            CSV content as bytes.

        Raises:
            ValueError: If JSON is invalid or cannot be converted.
        """
        if export_mode == ExportMode.SINGLE_ROW:
            df = self._json_to_dataframe_single_row(content)
        elif export_mode == ExportMode.MULTI_TABLE:
            # Multi-table returns dict of DataFrames, handle in subclass or main.py
            # For CSV, this will be handled separately (ZIP file)
            raise ValueError(
                "MULTI_TABLE mode for CSV requires special handling (ZIP output)."
            )
        else:
            df = self._json_to_dataframe(content)

        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue().encode("utf-8")

    def convert_multi_table(self, content: bytes) -> dict[str, pd.DataFrame]:
        """Convert JSON to multiple DataFrames (one per array).

        Args:
            content: JSON content as bytes.

        Returns:
            Dictionary mapping table names to DataFrames.
            Always includes a "main" table with scalar fields.

        Raises:
            ValueError: If JSON is invalid.
        """
        data = self._parse_json(content)

        if isinstance(data, list):
            if not data or not all(isinstance(item, dict) for item in data):
                raise ValueError("JSON must be an array of objects or a single object.")
            # For array of objects, process first item structure
            # and apply to all items
            return self._extract_tables_from_objects(data)

        elif isinstance(data, dict):
            return self._extract_tables_from_objects([data])

        raise ValueError("Invalid JSON structure.")

    def _extract_tables_from_objects(
        self, objects: list[dict[str, Any]]
    ) -> dict[str, pd.DataFrame]:
        """Extract multiple tables from a list of objects.

        Args:
            objects: List of JSON objects.

        Returns:
            Dictionary of table name -> DataFrame.
        """
        main_rows: list[dict[str, Any]] = []
        array_tables: dict[str, list[dict[str, Any]]] = {}

        for idx, obj in enumerate(objects):
            record_id = idx + 1
            main_row = {"_record_id": record_id}

            for key, value in obj.items():
                if isinstance(value, dict):
                    # Flatten nested objects into main row
                    flat = self._flatten_dict(value, f"{key}.")
                    main_row.update(flat)

                elif isinstance(value, list):
                    if value and all(isinstance(item, dict) for item in value):
                        # Array of objects -> separate table
                        table_name = key
                        if table_name not in array_tables:
                            array_tables[table_name] = []

                        for item in value:
                            row = {"_record_id": record_id}
                            flat = self._flatten_dict(item)
                            row.update(flat)
                            array_tables[table_name].append(row)
                    else:
                        # Array of primitives -> JSON string in main
                        main_row[key] = json.dumps(value) if value else "[]"

                else:
                    # Scalar value
                    main_row[key] = value

            main_rows.append(main_row)

        # Build result dictionary
        result: dict[str, pd.DataFrame] = {"main": pd.DataFrame(main_rows)}

        for table_name, rows in array_tables.items():
            if rows:
                result[table_name] = pd.DataFrame(rows)

        return result

    def _flatten_dict(
        self, obj: dict[str, Any], prefix: str = ""
    ) -> dict[str, Any]:
        """Flatten a nested dictionary using dot notation.

        Args:
            obj: Dictionary to flatten.
            prefix: Prefix for keys.

        Returns:
            Flattened dictionary.
        """
        result: dict[str, Any] = {}

        for key, value in obj.items():
            full_key = f"{prefix}{key}"

            if isinstance(value, dict):
                result.update(self._flatten_dict(value, f"{full_key}."))
            elif isinstance(value, list):
                result[full_key] = json.dumps(value) if value else "[]"
            else:
                result[full_key] = value

        return result

    def preview(
        self,
        content: bytes,
        page: int = 1,
        page_size: int = 10,
        export_mode: ExportMode = ExportMode.NORMAL,
    ) -> dict[str, Any]:
        """Generate preview of JSON data with pagination.

        Args:
            content: JSON content as bytes.
            page: Page number (1-indexed). Defaults to 1.
            page_size: Number of rows per page. Defaults to 10.
            export_mode: Export mode (NORMAL, MULTI_TABLE, or SINGLE_ROW).

        Returns:
            Preview dictionary with columns, rows, total_rows, and pagination info.
            For MULTI_TABLE mode, includes table_info with counts per table.
        """
        if export_mode == ExportMode.SINGLE_ROW:
            df = self._json_to_dataframe_single_row(content)
        elif export_mode == ExportMode.MULTI_TABLE:
            tables = self.convert_multi_table(content)
            # Preview the main table, but include info about other tables
            df = tables.get("main", pd.DataFrame())
            table_info = {name: len(tdf) for name, tdf in tables.items()}
        else:
            df = self._json_to_dataframe(content)

        total_rows = len(df)
        total_pages = max(1, (total_rows + page_size - 1) // page_size)

        # Ensure page is within bounds
        page = max(1, min(page, total_pages))

        # Calculate slice indices
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        # Get the page slice
        page_df = df.iloc[start_idx:end_idx]

        result = {
            "columns": df.columns.tolist(),
            "rows": page_df.values.tolist(),
            "total_rows": total_rows,
            "current_page": page,
            "total_pages": total_pages,
            "page_size": page_size,
        }

        # Add table info for multi-table mode
        if export_mode == ExportMode.MULTI_TABLE:
            result["table_info"] = table_info
            result["preview_table"] = "main"

        return result

    def _json_to_dataframe_single_row(self, content: bytes) -> pd.DataFrame:
        """Convert JSON to DataFrame keeping arrays as JSON strings.

        Each root object becomes a single row, with arrays serialized
        as JSON strings rather than expanded.

        Args:
            content: JSON content as bytes.

        Returns:
            A pandas DataFrame with one row per root object.

        Raises:
            ValueError: If JSON cannot be parsed.
        """
        data = self._parse_json(content)

        if isinstance(data, list):
            if not data:
                raise ValueError("JSON array is empty.")
            if not all(isinstance(item, dict) for item in data):
                raise ValueError("JSON array must contain objects.")

            rows = [self._flatten_object_single_row(item) for item in data]
            return pd.DataFrame(rows)

        elif isinstance(data, dict):
            row = self._flatten_object_single_row(data)
            return pd.DataFrame([row])

        raise ValueError("Invalid JSON structure.")

    def _flatten_object_single_row(
        self, obj: dict[str, Any], prefix: str = ""
    ) -> dict[str, Any]:
        """Flatten an object to a single row, keeping arrays as JSON strings.

        Args:
            obj: The object to flatten.
            prefix: Prefix for nested keys.

        Returns:
            A flat dictionary (single row).
        """
        result: dict[str, Any] = {}

        for key, value in obj.items():
            full_key = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                # Recursively flatten nested objects
                nested = self._flatten_object_single_row(value, f"{full_key}.")
                result.update(nested)

            elif isinstance(value, list):
                # Keep arrays as JSON strings (no expansion)
                result[full_key] = json.dumps(value) if value else "[]"

            else:
                # Scalar value
                result[full_key] = value

        return result

    def preview_all_tables(
        self,
        content: bytes,
        rows_per_table: int = 5,
    ) -> dict[str, Any]:
        """Preview all tables from complex JSON for multi-table mode.

        Returns a limited number of rows from each table to allow
        users to preview the multi-table structure before downloading.

        Args:
            content: JSON content as bytes.
            rows_per_table: Maximum rows to return per table. Defaults to 5.

        Returns:
            Dictionary with:
            {
                "tables": {
                    "main": {"columns": [...], "rows": [...], "total_rows": int},
                    "array_name": {"columns": [...], "rows": [...], "total_rows": int},
                    ...
                }
            }

        Raises:
            ValueError: If JSON is invalid.
        """
        tables = self.convert_multi_table(content)

        result: dict[str, Any] = {}
        for table_name, df in tables.items():
            result[table_name] = {
                "columns": df.columns.tolist(),
                "rows": df.head(rows_per_table).values.tolist(),
                "total_rows": len(df),
            }

        return {"tables": result}

    def _parse_json(self, content: bytes) -> Any:
        """Parse JSON content from bytes.

        Args:
            content: JSON content as bytes.

        Returns:
            Parsed JSON data.

        Raises:
            ValueError: If JSON is invalid.
        """
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError(
                f"File encoding error: Unable to decode as UTF-8. Details: {e}"
            ) from e

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}"
            ) from e

    def _json_to_dataframe(self, content: bytes) -> pd.DataFrame:
        """Parse JSON and convert to DataFrame.

        Handles arrays of objects and expands nested arrays into multiple rows
        using Cartesian product (denormalization).

        Args:
            content: JSON content as bytes.

        Returns:
            A pandas DataFrame.

        Raises:
            ValueError: If JSON cannot be parsed or converted.
        """
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError(
                f"File encoding error: Unable to decode as UTF-8. "
                f"Please ensure the file is saved with UTF-8 encoding. Details: {e}"
            ) from e

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}"
            ) from e

        # Handle different JSON structures
        if isinstance(data, list):
            if not data:
                raise ValueError(
                    "JSON array is empty. The file contains '[]' with no data."
                )
            # Check if items are objects
            if not all(isinstance(item, dict) for item in data):
                raise ValueError(
                    "JSON array must contain objects. Found non-object items in array."
                )
            # Expand each object and combine all rows
            all_rows: list[dict[str, Any]] = []
            for item in data:
                all_rows.extend(self._expand_object(item))
            self._check_row_limit(len(all_rows))
            return pd.DataFrame(all_rows)

        elif isinstance(data, dict):
            # Single object - expand it fully
            rows = self._expand_object(data)
            self._check_row_limit(len(rows))
            return pd.DataFrame(rows)

        else:
            raise ValueError(
                f"Invalid JSON structure. Expected an array of objects or an object, "
                f"but got {type(data).__name__}."
            )

    def _check_row_limit(self, row_count: int) -> None:
        """Check if row count exceeds the safety limit.

        Args:
            row_count: Number of rows generated.

        Raises:
            ValueError: If row count exceeds MAX_EXPANDED_ROWS.
        """
        if row_count > MAX_EXPANDED_ROWS:
            raise ValueError(
                f"Expansion would create {row_count} rows (limit: {MAX_EXPANDED_ROWS}). "
                f"The nested arrays in your JSON create too many combinations. "
                f"Consider simplifying your JSON structure or processing it in parts."
            )

    def _expand_object(
        self, obj: dict[str, Any], prefix: str = ""
    ) -> list[dict[str, Any]]:
        """Expand an object with nested arrays into multiple flat rows.

        Creates the Cartesian product of all nested arrays, producing one row
        per combination. Scalar fields are repeated in each row.

        Args:
            obj: The object to expand.
            prefix: Prefix for nested keys (used for dot notation).

        Returns:
            A list of flat dictionaries, one per row.
        """
        # Separate scalars from nested structures
        scalars: dict[str, Any] = {}
        array_expansions: list[tuple[str, list[dict[str, Any]]]] = []

        for key, value in obj.items():
            full_key = f"{prefix}{key}"

            if isinstance(value, dict):
                # Recursively expand nested objects
                nested_rows = self._expand_object(value, f"{full_key}.")
                if len(nested_rows) == 1:
                    # Single row - merge into scalars
                    scalars.update(nested_rows[0])
                else:
                    # Multiple rows - add to array expansions
                    array_expansions.append((full_key, nested_rows))

            elif isinstance(value, list):
                if value and all(isinstance(item, dict) for item in value):
                    # Array of objects - expand each item with key prefix
                    expanded_items: list[dict[str, Any]] = []
                    for item in value:
                        item_rows = self._expand_object(item, f"{full_key}.")
                        expanded_items.extend(item_rows)
                    array_expansions.append((full_key, expanded_items))
                elif value:
                    # Array of primitives - convert to JSON string
                    scalars[full_key] = json.dumps(value)
                else:
                    # Empty array
                    scalars[full_key] = "[]"

            else:
                # Scalar value
                scalars[full_key] = value

        # If no arrays to expand, return single row with scalars
        if not array_expansions:
            return [scalars] if scalars else [{}]

        # Compute Cartesian product of all array expansions
        array_rows_list = [rows for _, rows in array_expansions]
        product = list(itertools.product(*array_rows_list))

        # Combine scalars with each product combination
        result: list[dict[str, Any]] = []
        for combination in product:
            row = scalars.copy()
            for expanded_row in combination:
                row.update(expanded_row)
            result.append(row)

        return result if result else [scalars]
