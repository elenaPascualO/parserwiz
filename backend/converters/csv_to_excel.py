"""CSV to Excel converter."""

import io

import pandas as pd

from backend.converters.csv_to_json import CsvToJsonConverter


class CsvToExcelConverter(CsvToJsonConverter):
    """Converts CSV data to Excel format.

    Inherits CSV parsing logic from CsvToJsonConverter.
    """

    def convert(self, content: bytes) -> bytes:
        """Convert CSV to Excel (.xlsx).

        Args:
            content: CSV content as bytes.

        Returns:
            Excel content as bytes.

        Raises:
            ValueError: If CSV is invalid or cannot be converted.
        """
        df = self._csv_to_dataframe(content)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        return output.getvalue()
