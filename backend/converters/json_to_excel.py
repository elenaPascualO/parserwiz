"""JSON to Excel converter."""

import io

import pandas as pd

from backend.converters.json_to_csv import JsonToCsvConverter


class JsonToExcelConverter(JsonToCsvConverter):
    """Converts JSON data to Excel format.

    Inherits JSON parsing logic from JsonToCsvConverter.
    """

    def convert(self, content: bytes) -> bytes:
        """Convert JSON to Excel (.xlsx).

        Args:
            content: JSON content as bytes.

        Returns:
            Excel content as bytes.

        Raises:
            ValueError: If JSON is invalid or cannot be converted.
        """
        df = self._json_to_dataframe(content)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        return output.getvalue()
