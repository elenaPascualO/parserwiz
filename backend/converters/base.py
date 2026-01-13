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
    def preview(
        self, content: bytes, page: int = 1, page_size: int = 10
    ) -> dict[str, Any]:
        """Generate a preview of the file content with pagination.

        Args:
            content: The file content as bytes.
            page: Page number (1-indexed). Defaults to 1.
            page_size: Number of rows per page. Defaults to 10.

        Returns:
            A dictionary with preview data:
            {
                "columns": ["col1", "col2", ...],
                "rows": [["val1", "val2", ...], ...],
                "total_rows": 100,
                "current_page": 1,
                "total_pages": 10,
                "page_size": 10
            }
        """
        pass
