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

    def preview(
        self, content: bytes, page: int = 1, page_size: int = 10
    ) -> dict[str, Any]:
        """Generate preview of CSV data with pagination.

        Args:
            content: CSV content as bytes.
            page: Page number (1-indexed). Defaults to 1.
            page_size: Number of rows per page. Defaults to 10.

        Returns:
            Preview dictionary with columns, rows, total_rows, and pagination info.
        """
        # Read as strings to preserve original formatting (e.g., "007" stays "007")
        df = self._csv_to_dataframe(content, dtype=str)
        total_rows = len(df)
        total_pages = max(1, (total_rows + page_size - 1) // page_size)

        # Ensure page is within bounds
        page = max(1, min(page, total_pages))

        # Calculate slice indices
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        # Get the page slice and replace NaN with None
        page_df = df.iloc[start_idx:end_idx]
        page_df = page_df.where(pd.notna(page_df), None)

        return {
            "columns": df.columns.tolist(),
            "rows": page_df.values.tolist(),
            "total_rows": total_rows,
            "current_page": page,
            "total_pages": total_pages,
            "page_size": page_size,
        }

    def _csv_to_dataframe(
        self, content: bytes, dtype: type | None = None
    ) -> pd.DataFrame:
        """Parse CSV content to DataFrame with auto-detected delimiter.

        Args:
            content: CSV content as bytes.
            dtype: Data type to force for all columns (e.g., str for preview).

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
            raise ValueError(
                "Unable to read file: unsupported character encoding. "
                "Please save the file as UTF-8 and try again."
            )

        # Auto-detect delimiter
        delimiter = self._detect_delimiter(text)

        try:
            df = pd.read_csv(io.StringIO(text), sep=delimiter, dtype=dtype)
        except pd.errors.EmptyDataError:
            raise ValueError(
                "CSV file is empty. The file contains no data to convert."
            )
        except pd.errors.ParserError as e:
            error_msg = str(e)
            # Extract row number if present in error
            if "line" in error_msg.lower():
                raise ValueError(
                    f"CSV parsing error: {error_msg}. "
                    f"Check that all rows have the same number of columns."
                ) from e
            raise ValueError(
                f"Invalid CSV format: {error_msg}. "
                f"Ensure the file is a valid CSV with consistent delimiters."
            ) from e

        if df.empty:
            raise ValueError(
                "CSV file has headers but no data rows. "
                "Please add data below the header row."
            )

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
