"""Tests for API client error sanitization."""

import pytest

from mcp_server.api_client import _sanitize_error_details


class TestSanitizeErrorDetails:
    """Test HTML stripping and truncation of error details."""

    def test_html_error_page_stripped(self):
        """Full HTML error page should be stripped to text content."""
        html = """<!DOCTYPE html>
<html>
<head><title>Not Found</title></head>
<body>
<h1>Not Found</h1>
<p>The requested resource was not found on this server.</p>
</body>
</html>"""
        result = _sanitize_error_details(html)
        assert "<html" not in result
        assert "<body" not in result
        assert "<h1>" not in result
        assert "Not Found" in result

    def test_json_dict_preserved(self):
        """Dict details (from response.json()) should pass through unchanged."""
        details = {"error": "Not found", "code": 404}
        result = _sanitize_error_details(details)
        assert result == details

    def test_plain_text_preserved(self):
        """Plain text error message should pass through."""
        text = "Connection refused by upstream server"
        result = _sanitize_error_details(text)
        assert result == text

    def test_long_text_truncated(self):
        """Strings longer than 500 chars should be truncated."""
        long_text = "x" * 1000
        result = _sanitize_error_details(long_text)
        assert len(result) == 503  # 500 + "..."
        assert result.endswith("...")

    def test_empty_html_fallback(self):
        """HTML with no text content should return fallback message."""
        html = "<html><body></body></html>"
        result = _sanitize_error_details(html)
        assert result == "HTML error page (no extractable text)"

    def test_django_debug_page_stripped(self):
        """Django debug 404 page (large HTML) should be stripped and truncated."""
        html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Page not found at /api/v1/services/</title></head>
<body>
<div id="summary">
  <h1>Page not found <span>(404)</span></h1>
  <table class="meta"><tr><th>Request Method:</th><td>GET</td></tr>
  <tr><th>Request URL:</th><td>https://app.ayna.com/api/v1/services/</td></tr></table>
</div>
<div id="info">
  <p>Using the URLconf defined in <code>config.urls</code>, Django tried these URL patterns...</p>
  <p>The current path, <code>api/v1/services/</code>, didn't match any of these.</p>
</div>
</body>
</html>"""
        result = _sanitize_error_details(html)
        assert "<html" not in result
        assert "<div" not in result
        assert "Page not found" in result
        assert len(result) <= 503  # max 500 + "..."
