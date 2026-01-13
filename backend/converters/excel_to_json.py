"""Excel to JSON converter."""

import io
import json
from typing import Any

import pandas as pd

from backend.converters.base import BaseConverter


class ExcelToJsonConverter(BaseConverter):
    """Converts Excel data to JSON format."""

    def convert(self, content: bytes) -> bytes:
        """Convert Excel to JSON.

        Args:
            content: Excel content as bytes (.xlsx or .xls).

        Returns:
            JSON content as bytes (array of objects).

        Raises:
            ValueError: If Excel file is invalid or cannot be converted.
        """
        df = self._excel_to_dataframe(content)
        # Convert to list of dicts, handling NaN values
        records = df.to_dict(orient="records")
        # Replace NaN with None
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        return json.dumps(records, indent=2, ensure_ascii=False).encode("utf-8")

    def preview(self, content: bytes, rows: int = 10) -> dict[str, Any]:
        """Generate preview of Excel data.

        Args:
            content: Excel content as bytes.
            rows: Maximum rows to preview.

        Returns:
            Preview dictionary with columns, rows, and total_rows.
        """
        df = self._excel_to_dataframe(content)
        # Replace NaN with None for JSON serialization
        preview_df = df.head(rows).where(pd.notna(df.head(rows)), None)
        return {
            "columns": df.columns.tolist(),
            "rows": preview_df.values.tolist(),
            "total_rows": len(df),
        }

    def _excel_to_dataframe(self, content: bytes) -> pd.DataFrame:
        """Parse Excel content to DataFrame.

        Reads the first sheet of the Excel file.

        Args:
            content: Excel content as bytes.

        Returns:
            A pandas DataFrame.

        Raises:
            ValueError: If Excel file cannot be parsed.
        """
        try:
            # Try xlsx first (openpyxl)
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        except Exception:
            try:
                # Fall back to xls (xlrd)
                df = pd.read_excel(io.BytesIO(content), engine="xlrd")
            except Exception as e:
                raise ValueError(f"Could not read Excel file: {e}") from e

        if df.empty:
            raise ValueError("Excel file has no data")

        return df
