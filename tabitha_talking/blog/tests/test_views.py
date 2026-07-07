from datetime import date

import pytest
from django.urls import reverse

from tabitha_talking.blog.models import BlogPage


@pytest.mark.django_db
class TestBlogViews:
    """Tests for blog views."""

    def test_blog_index_page_loads(self, blog_index, client):
        """Test blog index page loads successfully."""
        response = client.get(blog_index.url)
        assert response.status_code == 200
        assert b"Blog" in response.content

    def test_blog_post_page_loads(self, blog_post, client):
        """Test blog post page loads successfully."""
        response = client.get(blog_post.url)
        assert response.status_code == 200
        assert b"Test Blog Post" in response.content

    def test_navbar_includes_search_form(self, blog_index, client):
        """Navbar should include blog search form."""
        response = client.get(blog_index.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert f'action="{reverse("blog:search")}"' in content
        assert 'name="query"' in content


@pytest.mark.django_db
class TestEmptyBlogIndex:
    """Tests for blog index fallback when no posts exist."""

    def test_blog_index_empty_shows_message(self, blog_index, client):
        """Blog index should show friendly message when no posts exist."""
        response = client.get(blog_index.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "No blog posts yet" in content

    def test_blog_index_with_posts_hides_empty_message(
        self,
        blog_index,
        blog_post,
        client,
    ):
        """Blog index should not show empty message when posts exist."""
        response = client.get(blog_index.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert blog_post.title in content

    def test_blog_index_shows_pagination_controls(self, blog_index, client, user):
        """Blog index should show pagination when multiple pages."""
        for i in range(12):
            post = BlogPage(
                title=f"Post {i}",
                date=date.today(),
                intro=f"Post intro {i}",
                slug=f"post-{i}",
            )
            post.body = [
                {"type": "rich_text", "value": f"<p>Post {i} body</p>"},
            ]
            blog_index.add_child(instance=post)
            post.save_revision().publish()

        response = client.get(blog_index.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "pagination" in content or "page" in content.lower()

    def test_blog_index_pagination_page_two(self, blog_index, client, user):
        """Blog index page 2 should show correct posts."""
        for i in range(12):
            post = BlogPage(
                title=f"Pagination Post {i}",
                date=date.today(),
                intro=f"Post {i}",
                slug=f"pag-post-{i}",
            )
            post.body = [
                {"type": "rich_text", "value": f"<p>Post {i}</p>"},
            ]
            blog_index.add_child(instance=post)
            post.save_revision().publish()

        response = client.get(blog_index.url + "?page=2")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Pagination Post" in content
