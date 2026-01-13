"""Excel to CSV converter."""

import io


from backend.converters.excel_to_json import ExcelToJsonConverter


class ExcelToCsvConverter(ExcelToJsonConverter):
    """Converts Excel data to CSV format.

    Inherits Excel parsing logic from ExcelToJsonConverter.
    """

    def convert(self, content: bytes) -> bytes:
        """Convert Excel to CSV.

        Args:
            content: Excel content as bytes (.xlsx or .xls).

        Returns:
            CSV content as bytes.

        Raises:
            ValueError: If Excel file is invalid or cannot be converted.
        """
        df = self._excel_to_dataframe(content)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue().encode("utf-8")
