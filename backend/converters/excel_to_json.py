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

    def preview(
        self, content: bytes, page: int = 1, page_size: int = 10
    ) -> dict[str, Any]:
        """Generate preview of Excel data with pagination.

        Args:
            content: Excel content as bytes.
            page: Page number (1-indexed). Defaults to 1.
            page_size: Number of rows per page. Defaults to 10.

        Returns:
            Preview dictionary with columns, rows, total_rows, and pagination info.
        """
        # Read as strings to preserve original formatting (e.g., "007" stays "007")
        df = self._excel_to_dataframe(content, dtype=str)
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

    def _excel_to_dataframe(
        self, content: bytes, dtype: type | None = None
    ) -> pd.DataFrame:
        """Parse Excel content to DataFrame.

        Reads the first sheet of the Excel file.

        Args:
            content: Excel content as bytes.
            dtype: Data type to force for all columns (e.g., str for preview).

        Returns:
            A pandas DataFrame.

        Raises:
            ValueError: If Excel file cannot be parsed.
        """
        xlsx_error = None
        xls_error = None

        try:
            # Try xlsx first (openpyxl)
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl", dtype=dtype)
        except Exception as e:
            xlsx_error = str(e)
            try:
                # Fall back to xls (xlrd)
                df = pd.read_excel(io.BytesIO(content), engine="xlrd", dtype=dtype)
            except Exception as e2:
                xls_error = str(e2)
                # Provide helpful error message based on the errors
                if "File is not a zip file" in xlsx_error:
                    raise ValueError(
                        "Invalid Excel file: The file appears to be corrupted or "
                        "is not a valid Excel file. Please check that the file "
                        "opens correctly in Excel."
                    ) from e2
                elif "Unsupported format" in xls_error or "not supported" in xls_error.lower():
                    raise ValueError(
                        "Unsupported Excel format. Please save the file as .xlsx "
                        "(Excel 2007+) or .xls (Excel 97-2003) format."
                    ) from e2
                else:
                    raise ValueError(
                        f"Could not read Excel file. The file may be corrupted, "
                        f"password-protected, or in an unsupported format. "
                        f"Details: {xlsx_error}"
                    ) from e2

        if df.empty:
            raise ValueError(
                "Excel file has no data. The first sheet is empty or contains "
                "only headers with no data rows."
            )

        return df
