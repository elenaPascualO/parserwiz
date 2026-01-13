"""CSV to JSON converter."""

import io
import json
from typing import Any

import pandas as pd

from backend.converters.base import BaseConverter


class CsvToJsonConverter(BaseConverter):
    """Converts CSV data to JSON format."""

    def convert(self, content: bytes) -> bytes:
        """Convert CSV to JSON.

        Args:
            content: CSV content as bytes.

        Returns:
            JSON content as bytes (array of objects).

        Raises:
            ValueError: If CSV is invalid or cannot be converted.
        """
        df = self._csv_to_dataframe(content)
        # Convert to list of dicts, handling NaN values
        records = df.to_dict(orient="records")
        # Replace NaN with None (NaN != NaN is True)
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        return json.dumps(records, indent=2, ensure_ascii=False).encode("utf-8")

    def preview(self, content: bytes, rows: int = 10) -> dict[str, Any]:
        """Generate preview of CSV data.

        Args:
            content: CSV content as bytes.
            rows: Maximum rows to preview.

        Returns:
            Preview dictionary with columns, rows, and total_rows.
        """
        df = self._csv_to_dataframe(content)
        # Replace NaN with None for JSON serialization
        preview_df = df.head(rows).where(pd.notna(df.head(rows)), None)
        return {
            "columns": df.columns.tolist(),
            "rows": preview_df.values.tolist(),
            "total_rows": len(df),
        }

    def _csv_to_dataframe(self, content: bytes) -> pd.DataFrame:
        """Parse CSV content to DataFrame with auto-detected delimiter.

        Args:
            content: CSV content as bytes.

        Returns:
            A pandas DataFrame.

        Raises:
            ValueError: If CSV cannot be parsed.
        """
        # Try different encodings
        text = None
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if text is None:
            raise ValueError("Could not decode file. Unsupported encoding.")

        # Auto-detect delimiter
        delimiter = self._detect_delimiter(text)

        try:
            df = pd.read_csv(io.StringIO(text), sep=delimiter)
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Invalid CSV format: {e}") from e

        if df.empty:
            raise ValueError("CSV file has no data rows")

        return df

    def _detect_delimiter(self, text: str) -> str:
        """Auto-detect the CSV delimiter.

        Args:
            text: The CSV text content.

        Returns:
            The detected delimiter character.
        """
        # Get first line
        first_line = text.split("\n")[0] if "\n" in text else text

        # Count potential delimiters
        delimiters = {
            ",": first_line.count(","),
            ";": first_line.count(";"),
            "\t": first_line.count("\t"),
        }

        # Return delimiter with highest count, default to comma
        best_delimiter = max(delimiters, key=delimiters.get)
        return best_delimiter if delimiters[best_delimiter] > 0 else ","
