"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
def sample_files_dir() -> Path:
    """Return the path to sample files directory."""
    return Path(__file__).parent / "sample_files"


@pytest.fixture
def simple_json(sample_files_dir: Path) -> bytes:
    """Return simple JSON test data."""
    return (sample_files_dir / "simple.json").read_bytes()


@pytest.fixture
def nested_json(sample_files_dir: Path) -> bytes:
    """Return nested JSON test data."""
    return (sample_files_dir / "nested.json").read_bytes()


@pytest.fixture
def simple_csv(sample_files_dir: Path) -> bytes:
    """Return simple CSV test data."""
    return (sample_files_dir / "simple.csv").read_bytes()


@pytest.fixture
def nested2_json(sample_files_dir: Path) -> bytes:
    """Return nested2 JSON test data (single object with multiple arrays)."""
    return (sample_files_dir / "nested2.json").read_bytes()


@pytest.fixture
def nested3_json(sample_files_dir: Path) -> bytes:
    """Return nested3 JSON test data (array of objects with nested arrays)."""
    return (sample_files_dir / "nested3.json").read_bytes()


@pytest.fixture
def simple_xlsx(sample_files_dir: Path) -> bytes:
    """Return simple XLSX test data."""
    xlsx_path = sample_files_dir / "simple.xlsx"
    if xlsx_path.exists():
        return xlsx_path.read_bytes()
    # Generate if not exists
    import io

    import pandas as pd

    df = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [30, 25, 35],
            "city": ["New York", "Los Angeles", "Chicago"],
        }
    )
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    content = output.getvalue()
    # Save for future tests
    xlsx_path.write_bytes(content)
    return content


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
