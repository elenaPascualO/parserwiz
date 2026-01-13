"""Base converter class."""

from abc import ABC, abstractmethod
from typing import Any


class BaseConverter(ABC):
    """Abstract base class for file converters."""

    @abstractmethod
    def convert(self, content: bytes) -> bytes:
        """Convert file content to the target format.

        Args:
            content: The source file content as bytes.

        Returns:
            The converted file content as bytes.

        Raises:
            ValueError: If the content cannot be converted.
        """
        pass

    @abstractmethod
    def preview(self, content: bytes, rows: int = 10) -> dict[str, Any]:
        """Generate a preview of the file content.

        Args:
            content: The file content as bytes.
            rows: Maximum number of rows to include in preview.

        Returns:
            A dictionary with preview data:
            {
                "columns": ["col1", "col2", ...],
                "rows": [["val1", "val2", ...], ...],
                "total_rows": 100
            }
        """
        pass
