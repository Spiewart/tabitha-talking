"""Input validation and sanitization utilities."""

import re

MAX_EMAIL_LENGTH = 254


def sanitize_html(html_content: str) -> str:
    """Sanitize HTML to prevent XSS attacks by removing dangerous tags.

    Args:
        html_content: Raw HTML string

    Returns:
        Sanitized HTML string with dangerous tags removed
    """
    if not isinstance(html_content, str):
        return ""

    # Remove script tags and content
    sanitized = re.sub(
        r"<script[^>]*>.*?</script>",
        "",
        html_content,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Remove event handlers
    sanitized = re.sub(
        r'\s+on\w+\s*=\s*["\']?[^"\'>\s]+["\']?',
        "",
        sanitized,
        flags=re.IGNORECASE,
    )

    # Remove iframe tags
    sanitized = re.sub(
        r"<iframe[^>]*>.*?</iframe>",
        "",
        sanitized,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Remove style tags
    return re.sub(
        r"<style[^>]*>.*?</style>",
        "",
        sanitized,
        flags=re.DOTALL | re.IGNORECASE,
    )


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format and length.

    Args:
        email: Email string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(email, str) or not email.strip():
        return False, "Email must be a non-empty string"

    email = email.strip().lower()

    if len(email) > MAX_EMAIL_LENGTH:
        return False, f"Email exceeds maximum length of {MAX_EMAIL_LENGTH}"

    if email.count("@") != 1:
        return False, "Invalid email format"

    local, domain = email.rsplit("@", 1)

    if not local or not domain or len(local) > 64 or "." not in domain:
        return False, "Invalid email format"

    return True, ""
