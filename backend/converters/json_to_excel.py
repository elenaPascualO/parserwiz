"""JSON to Excel converter."""

import io

import pandas as pd

from backend.converters.json_to_csv import ExportMode, JsonToCsvConverter


class JsonToExcelConverter(JsonToCsvConverter):
    """Converts JSON data to Excel format.

    Inherits JSON parsing logic from JsonToCsvConverter.
    """

    def convert(
        self, content: bytes, export_mode: ExportMode = ExportMode.NORMAL
    ) -> bytes:
        """Convert JSON to Excel (.xlsx).

        Args:
            content: JSON content as bytes.
            export_mode: Export mode (NORMAL, MULTI_TABLE, or SINGLE_ROW).

        Returns:
            Excel content as bytes.

        Raises:
            ValueError: If JSON is invalid or cannot be converted.
        """
        output = io.BytesIO()

        if export_mode == ExportMode.MULTI_TABLE:
            # Multi-table: one sheet per array
            tables = self.convert_multi_table(content)
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                for table_name, df in tables.items():
                    # Excel sheet names have 31 char limit
                    sheet_name = table_name[:31] if len(table_name) > 31 else table_name
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        elif export_mode == ExportMode.SINGLE_ROW:
            df = self._json_to_dataframe_single_row(content)
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Data", index=False)

        else:
            # Normal mode
            df = self._json_to_dataframe(content)
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Data", index=False)

        return output.getvalue()
