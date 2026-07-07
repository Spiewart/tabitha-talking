import pytest
from django.test import RequestFactory

from tabitha_talking.blog.models import BlogPage


@pytest.mark.django_db
class TestBlogModels:
    """Tests for blog models."""

    def test_blog_index_page_creation(self, blog_index):
        """Test blog index page is created."""
        assert blog_index.title == "Blog"
        assert blog_index.live

    def test_blog_page_creation(self, blog_post):
        """Test blog page is created."""
        assert blog_post.title == "Test Blog Post"
        assert blog_post.intro == "This is a test blog post"
        assert blog_post.live

    def test_blog_index_page_get_context_with_posts(self, blog_index, blog_post):
        """Test blog index page context includes blog posts."""
        rf = RequestFactory()
        request = rf.get("/")
        context = blog_index.get_context(request)
        assert "blogpages" in context
        blogpages = list(context["blogpages"])
        assert len(blogpages) == 1
        assert blogpages[0].title == "Test Blog Post"

    def test_blog_index_page_get_context_ordered_by_date(self, blog_index):
        """Test blog posts are ordered by date (newest first)."""
        from datetime import date
        from datetime import timedelta

        older_post = BlogPage(
            title="Older Post",
            date=date.today() - timedelta(days=5),
            intro="Older post",
            slug="older-post",
        )
        older_post.body = [{"type": "rich_text", "value": "<p>Older content</p>"}]
        blog_index.add_child(instance=older_post)
        older_post.save_revision().publish()

        newer_post = BlogPage(
            title="Newer Post",
            date=date.today(),
            intro="Newer post",
            slug="newer-post",
        )
        newer_post.body = [{"type": "rich_text", "value": "<p>Newer content</p>"}]
        blog_index.add_child(instance=newer_post)
        newer_post.save_revision().publish()

        rf = RequestFactory()
        request = rf.get("/")
        context = blog_index.get_context(request)
        blogpages = list(context["blogpages"])
        assert len(blogpages) == 2
        assert blogpages[0].title == "Newer Post"
        assert blogpages[1].title == "Older Post"
