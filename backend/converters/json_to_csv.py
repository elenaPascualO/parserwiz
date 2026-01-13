"""JSON to CSV converter."""

import io
import json
from typing import Any

import pandas as pd

from backend.converters.base import BaseConverter


class JsonToCsvConverter(BaseConverter):
    """Converts JSON data to CSV format."""

    def convert(self, content: bytes) -> bytes:
        """Convert JSON to CSV.

        Args:
            content: JSON content as bytes.

        Returns:
            CSV content as bytes.

        Raises:
            ValueError: If JSON is invalid or cannot be converted.
        """
        df = self._json_to_dataframe(content)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue().encode("utf-8")

    def preview(self, content: bytes, rows: int = 10) -> dict[str, Any]:
        """Generate preview of JSON data.

        Args:
            content: JSON content as bytes.
            rows: Maximum rows to preview.

        Returns:
            Preview dictionary with columns, rows, and total_rows.
        """
        df = self._json_to_dataframe(content)
        return {
            "columns": df.columns.tolist(),
            "rows": df.head(rows).values.tolist(),
            "total_rows": len(df),
        }

    def _json_to_dataframe(self, content: bytes) -> pd.DataFrame:
        """Parse JSON and convert to DataFrame.

        Handles arrays of objects and flattens first level of nesting.

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
            raise ValueError(f"Invalid encoding: {e}") from e

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e.msg}") from e

        # Handle different JSON structures
        if isinstance(data, list):
            if not data:
                raise ValueError("JSON array is empty")
            # Flatten first level of nesting
            flattened = [self._flatten_dict(item) for item in data]
            return pd.DataFrame(flattened)
        elif isinstance(data, dict):
            # Check if it's a single object or has array values
            # Try to find an array value to use as data
            for value in data.values():
                if isinstance(value, list) and value:
                    flattened = [self._flatten_dict(item) for item in value]
                    return pd.DataFrame(flattened)
            # Single object - convert to single row
            flattened = self._flatten_dict(data)
            return pd.DataFrame([flattened])
        else:
            raise ValueError("JSON must be an array of objects or an object")

    def _flatten_dict(self, d: dict[str, Any], parent_key: str = "") -> dict[str, Any]:
        """Flatten a dictionary by one level of nesting.

        Args:
            d: The dictionary to flatten.
            parent_key: Prefix for nested keys.

        Returns:
            A flattened dictionary.
        """
        items: list[tuple[str, Any]] = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                # Flatten one level - nested dicts become dot-notation keys
                for nested_k, nested_v in v.items():
                    nested_key = f"{new_key}.{nested_k}"
                    # Don't go deeper - convert deeper nesting to string
                    if isinstance(nested_v, (dict, list)):
                        items.append((nested_key, json.dumps(nested_v)))
                    else:
                        items.append((nested_key, nested_v))
            elif isinstance(v, list):
                # Convert lists to JSON string
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        return dict(items)
