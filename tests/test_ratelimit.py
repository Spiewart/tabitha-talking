"""Tests for rate limiting functionality."""

import pytest
from django.core.cache import cache

from config.ratelimit import get_client_ip
from config.ratelimit import get_identifier_for_user_action
from config.ratelimit import get_rate_limit_info
from config.ratelimit import is_rate_limited


@pytest.fixture
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestRateLimitingUtilities:
    """Test rate limiting utility functions."""

    def test_get_client_ip_from_remote_addr(self, rf):
        request = rf.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        assert get_client_ip(request) == "192.168.1.1"

    def test_get_client_ip_from_x_forwarded_for(self, rf):
        request = rf.get("/")
        request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.5, 198.51.100.2"
        assert get_client_ip(request) == "203.0.113.5"

    def test_get_client_ip_unknown(self, rf):
        request = rf.get("/")
        request.META.pop("REMOTE_ADDR", None)
        assert get_client_ip(request) == "unknown"

    def test_get_identifier_for_authenticated_user(self, rf, django_user_model):
        user = django_user_model.objects.create_user(
            username="testuser",
            password="pass",
        )
        request = rf.get("/")
        request.user = user
        identifier = get_identifier_for_user_action(request, "test_action")
        assert f"user:{user.id}" in identifier
        assert "ratelimit:test_action" in identifier

    def test_get_identifier_for_anonymous_user(self, rf):
        request = rf.get("/")
        request.user = None
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        identifier = get_identifier_for_user_action(request, "test_action")
        assert "ip:192.168.1.1" in identifier
        assert "ratelimit:test_action" in identifier

    def test_is_rate_limited_allows_first_attempt(self, rf, clear_cache):
        request = rf.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        result = is_rate_limited(
            request,
            "test_action",
            max_attempts=3,
            window_seconds=60,
        )
        assert result is False

    def test_is_rate_limited_allows_within_limit(self, rf, clear_cache):
        request = rf.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        for _i in range(3):
            result = is_rate_limited(
                request,
                "test_action",
                max_attempts=5,
                window_seconds=60,
            )
            assert result is False

    def test_is_rate_limited_blocks_over_limit(self, rf, clear_cache):
        request = rf.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        for _i in range(3):
            is_rate_limited(request, "test_action", max_attempts=3, window_seconds=60)
        result = is_rate_limited(
            request,
            "test_action",
            max_attempts=3,
            window_seconds=60,
        )
        assert result is True

    def test_is_rate_limited_different_actions(self, rf, clear_cache):
        request = rf.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        for _i in range(3):
            is_rate_limited(request, "action_a", max_attempts=3, window_seconds=60)
        result = is_rate_limited(request, "action_b", max_attempts=3, window_seconds=60)
        assert result is False

    def test_is_rate_limited_different_users(self, rf, django_user_model, clear_cache):
        user1 = django_user_model.objects.create_user(username="user1", password="pass")
        user2 = django_user_model.objects.create_user(username="user2", password="pass")

        request1 = rf.get("/")
        request1.user = user1
        for _i in range(3):
            is_rate_limited(request1, "test_action", max_attempts=3, window_seconds=60)

        request2 = rf.get("/")
        request2.user = user2
        result = is_rate_limited(
            request2,
            "test_action",
            max_attempts=3,
            window_seconds=60,
        )
        assert result is False

    def test_get_rate_limit_info(self, rf, clear_cache):
        request = rf.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        is_rate_limited(request, "test_action", max_attempts=5, window_seconds=60)
        is_rate_limited(request, "test_action", max_attempts=5, window_seconds=60)
        info = get_rate_limit_info(request, "test_action", max_attempts=5)
        assert info["remaining"] == 3
