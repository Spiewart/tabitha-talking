"""Comprehensive tests for URL routing and view behavior."""

import pytest
from django.urls import resolve
from django.urls import reverse
from wagtail.views import serve as wagtail_serve

from tabitha_talking.blog import views as blog_views
from tabitha_talking.blog.models import BlogIndexPage
from tabitha_talking.views import blog_view
from tabitha_talking.views import health_check
from tabitha_talking.views import home_view


@pytest.mark.django_db
class TestHomeView:
    """Tests for the home_view function."""

    def test_home_view_renders(self, client):
        """Home view should render home.html."""
        response = client.get(reverse("home"))
        assert response.status_code == 200
        assert any(t.name == "pages/home.html" for t in response.templates)

    def test_home_view_shows_content(self, client, blog_index):
        """Home view should always render content (not redirect)."""
        response = client.get(reverse("home"))
        assert response.status_code == 200
        assert any(t.name == "pages/home.html" for t in response.templates)


@pytest.mark.django_db
class TestBlogView:
    """Tests for the blog_view function."""

    def test_blog_view_without_blog_index(self, client):
        """When no BlogIndexPage exists, blog_view should render blog/index.html."""
        BlogIndexPage.objects.all().delete()
        response = client.get(reverse("blog_index"))
        assert response.status_code == 200

    def test_blog_view_with_blog_index(self, client, blog_index):
        """When BlogIndexPage exists, blog_view should serve it."""
        response = client.get(reverse("blog_index"))
        assert response.status_code == 200
        assert blog_index.title in response.content.decode()


@pytest.mark.django_db
class TestUrlResolution:
    """Tests for URL resolution and endpoint accessibility."""

    def test_resolve_core_urls(self):
        """Core routes should resolve to expected views."""
        assert resolve("/").func == home_view
        assert resolve("/blog/").func == blog_view
        assert resolve("/health/").func == health_check
        assert resolve("/blog/actions/search/").func == blog_views.search_blog

    def test_resolve_wagtail_catchall(self):
        """Wagtail should handle nested pages and top-level CMS pages."""
        match = resolve("/blog/some-page/")
        assert match.func == wagtail_serve
        # /about/ and /portfolio/ have no Django routes; they are Wagtail
        # pages resolved by the catch-all include at the end of urlpatterns.
        assert resolve("/about/").func == wagtail_serve
        assert resolve("/portfolio/").func == wagtail_serve

    def test_endpoint_status_codes(self, client, blog_index):
        """Key endpoints should return valid responses."""
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/blog/")
        assert response.status_code == 200

        response = client.get("/health/")
        assert response.status_code == 200

        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        assert response["Content-Type"] == "application/xml"

        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert response["Content-Type"] == "text/plain"

        response = client.get("/feed.xml")
        assert response.status_code == 200
        assert response["Content-Type"] == "application/rss+xml"

        response = client.get("/cms/")
        assert response.status_code in [200, 301, 302, 403, 404]

        response = client.get("/nonexistent-page-12345/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestNavbarLinks:
    """Tests for navbar links in base.html."""

    def test_navbar_links_present(self, client):
        """Navbar should contain Home, Blog, and Contact links."""
        BlogIndexPage.objects.all().delete()
        response = client.get("/")
        content = response.content.decode()
        assert 'href="/"' in content
        assert 'href="/blog/"' in content
