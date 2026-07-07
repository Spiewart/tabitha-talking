"""Tests for endpoint rate limiting."""

import pytest
from django.urls import reverse

from config.ratelimit import is_rate_limited


@pytest.mark.django_db
class TestSearchRateLimiting:
    """Test rate limiting on blog search endpoint."""

    def test_search_allows_multiple_queries_within_limit(self, client):
        """Search should allow multiple queries within rate limit."""
        for i in range(5):
            response = client.get(reverse("blog:search"), {"query": f"test{i}"})
            assert response.status_code == 200

    def test_search_blocks_excessive_queries(self, rf, clear_cache):
        """Search should block after exceeding rate limit."""
        from django.test import RequestFactory

        rf = RequestFactory()

        for i in range(31):
            request = rf.get(f"/blog/actions/search/?query=test{i}")
            request.META["REMOTE_ADDR"] = "192.168.1.1"
            request.user = None
            is_rate_limited(request, "blog_search", max_attempts=30, window_seconds=300)

        request = rf.get("/blog/actions/search/?query=final")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        request.user = None
        result = is_rate_limited(
            request,
            "blog_search",
            max_attempts=30,
            window_seconds=300,
        )
        assert result is True
