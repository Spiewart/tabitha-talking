"""Tests for input validation and sanitization."""

from config.validation import sanitize_html
from config.validation import validate_email


class TestHtmlSanitization:
    """Test HTML sanitization for XSS prevention."""

    def test_sanitize_html_removes_script_tags(self):
        dirty = "<p>Hello</p><script>alert('xss')</script>"
        clean = sanitize_html(dirty)
        assert "<script>" not in clean
        assert "alert" not in clean
        assert "<p>" in clean

    def test_sanitize_html_removes_event_handlers(self):
        dirty = "<p onclick=\"alert('xss')\">Click me</p>"
        clean = sanitize_html(dirty)
        assert "onclick" not in clean
        assert "alert" not in clean

    def test_sanitize_html_removes_iframes(self):
        dirty = '<p>Content</p><iframe src="evil.com"></iframe>'
        clean = sanitize_html(dirty)
        assert "<iframe>" not in clean
        assert "evil.com" not in clean

    def test_sanitize_html_removes_style_tags(self):
        dirty = (
            "<style>body { background: url('javascript:alert()'); }</style><p>Text</p>"
        )
        clean = sanitize_html(dirty)
        assert "<style>" not in clean

    def test_sanitize_html_preserves_safe_content(self):
        safe = "<p>Hello <strong>world</strong></p>"
        result = sanitize_html(safe)
        assert "<p>" in result
        assert "<strong>" in result

    def test_sanitize_html_handles_non_string(self):
        assert sanitize_html(None) == ""
        assert sanitize_html(123) == ""
        assert sanitize_html([]) == ""


class TestEmailValidation:
    """Test email validation."""

    def test_validate_email_valid(self):
        is_valid, error = validate_email("user@example.com")
        assert is_valid is True
        assert error == ""

    def test_validate_email_empty(self):
        is_valid, error = validate_email("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_email_no_at_sign(self):
        is_valid, _error = validate_email("userexample.com")
        assert is_valid is False

    def test_validate_email_no_domain_dot(self):
        is_valid, _error = validate_email("user@example")
        assert is_valid is False

    def test_validate_email_multiple_at_signs(self):
        is_valid, _error = validate_email("user@domain@example.com")
        assert is_valid is False

    def test_validate_email_too_long(self):
        is_valid, error = validate_email("x" * 300 + "@example.com")
        assert is_valid is False
        assert "exceeds" in error.lower()

    def test_validate_email_local_part_too_long(self):
        is_valid, _error = validate_email("x" * 100 + "@example.com")
        assert is_valid is False

    def test_validate_email_with_whitespace(self):
        is_valid, _error = validate_email("  user@example.com  ")
        assert is_valid is True

    def test_validate_email_non_string(self):
        is_valid, _error = validate_email(123)
        assert is_valid is False
