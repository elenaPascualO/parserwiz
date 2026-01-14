"""Tests for security utilities and middleware."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.utils.security import (
    encode_filename_header,
    sanitize_filename,
)


class TestSanitizeFilename:
    """Tests for filename sanitization."""

    def test_normal_filename(self):
        """Normal filename should be unchanged."""
        assert sanitize_filename("document.csv") == "document.csv"

    def test_empty_filename(self):
        """Empty filename should return default."""
        assert sanitize_filename("") == "download"
        assert sanitize_filename("   ") == "download"

    def test_removes_newlines(self):
        """Newlines should be replaced to prevent header injection."""
        assert sanitize_filename("file\nname.csv") == "file_name.csv"
        assert sanitize_filename("file\r\nname.csv") == "file__name.csv"

    def test_removes_quotes(self):
        """Double quotes should be replaced."""
        assert sanitize_filename('file"name.csv') == "file'name.csv"

    def test_removes_backslashes(self):
        """Backslashes should be replaced."""
        assert sanitize_filename("file\\name.csv") == "file_name.csv"

    def test_removes_forward_slashes(self):
        """Forward slashes should be replaced (path traversal)."""
        assert sanitize_filename("path/to/file.csv") == "file.csv"

    def test_removes_null_bytes(self):
        """Null bytes should be removed."""
        assert sanitize_filename("file\x00name.csv") == "filename.csv"

    def test_removes_control_characters(self):
        """Control characters should be removed."""
        assert sanitize_filename("file\x01\x02name.csv") == "filename.csv"

    def test_limits_length(self):
        """Long filenames should be truncated."""
        long_name = "a" * 300 + ".csv"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".csv")

    def test_preserves_extension_on_truncation(self):
        """Extension should be preserved when truncating."""
        long_name = "a" * 300 + ".xlsx"
        result = sanitize_filename(long_name)
        assert result.endswith(".xlsx")

    def test_header_injection_attempt(self):
        """Attempt to inject headers should be sanitized."""
        malicious = "file.csv\r\nX-Injected-Header: evil"
        result = sanitize_filename(malicious)
        assert "\r" not in result
        assert "\n" not in result
        assert "X-Injected-Header" not in result or "_" in result


class TestEncodeFilenameHeader:
    """Tests for Content-Disposition header encoding."""

    def test_ascii_filename(self):
        """ASCII filename should use simple quoted format."""
        result = encode_filename_header("document.csv")
        assert result == 'attachment; filename="document.csv"'

    def test_non_ascii_filename(self):
        """Non-ASCII filename should use RFC 5987 encoding."""
        result = encode_filename_header("documento_español.csv")
        assert result.startswith("attachment; filename*=UTF-8''")
        assert "documento" in result

    def test_sanitizes_before_encoding(self):
        """Should sanitize filename before encoding."""
        result = encode_filename_header("file\nname.csv")
        assert "\n" not in result

    def test_empty_filename(self):
        """Empty filename should use default."""
        result = encode_filename_header("")
        assert "download" in result


class TestSecurityHeadersMiddleware:
    """Tests for security headers in responses."""

    @pytest_asyncio.fixture
    async def test_client(self):
        """Create async test client."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_health_endpoint_has_security_headers(self, test_client):
        """Health endpoint should have security headers."""
        response = await test_client.get("/api/health")

        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "strict-origin" in response.headers.get("Referrer-Policy", "")

    @pytest.mark.asyncio
    async def test_preview_endpoint_has_security_headers(self, test_client, simple_json):
        """Preview endpoint should have security headers."""
        response = await test_client.post(
            "/api/preview",
            files={"file": ("test.json", simple_json, "application/json")},
        )

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"

    @pytest.mark.asyncio
    async def test_convert_endpoint_has_security_headers(self, test_client, simple_json):
        """Convert endpoint should have security headers."""
        response = await test_client.post(
            "/api/convert",
            files={"file": ("test.json", simple_json, "application/json")},
            data={"output_format": "csv"},
        )

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"


class TestConvertEndpointFilenameSanitization:
    """Tests for filename sanitization in convert endpoint."""

    @pytest_asyncio.fixture
    async def test_client(self):
        """Create async test client."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_normal_filename_in_response(self, test_client, simple_json):
        """Normal filename should appear in Content-Disposition."""
        response = await test_client.post(
            "/api/convert",
            files={"file": ("mydata.json", simple_json, "application/json")},
            data={"output_format": "csv"},
        )

        assert response.status_code == 200
        disposition = response.headers.get("Content-Disposition", "")
        assert "mydata.csv" in disposition

    @pytest.mark.asyncio
    async def test_malicious_filename_is_sanitized(self, test_client, simple_json):
        """Malicious filename should be sanitized."""
        # Attempt header injection via filename (keeping valid .json extension)
        # This tests that dangerous characters are sanitized in the output filename
        malicious_name = 'data"injection.json'

        response = await test_client.post(
            "/api/convert",
            files={"file": (malicious_name, simple_json, "application/json")},
            data={"output_format": "csv"},
        )

        assert response.status_code == 200
        disposition = response.headers.get("Content-Disposition", "")

        # Double quotes should be sanitized (replaced with single quotes)
        assert '"injection' not in disposition
        # Should still have attachment and the filename
        assert "attachment" in disposition
        assert "data" in disposition


@pytest.fixture
def simple_json():
    """Simple JSON test data."""
    return b'[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'