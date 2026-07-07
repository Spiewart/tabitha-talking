from django.core.paginator import InvalidPage
from django.core.paginator import Paginator
from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import MultiFieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import RichTextField
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index


class BlogIndexPage(Page):
    """Main blog page that lists all blog posts."""

    intro = RichTextField(blank=True)
    posts_per_page = 10

    # Only blog posts may live under the blog index, and there should be
    # exactly one blog index (it is served at /blog/ by blog_view).
    subpage_types = ["blog.BlogPage"]
    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        """Add blog posts to template context with pagination."""
        context = super().get_context(request)
        if self.pk:
            # Query the concrete BlogPage model directly instead of
            # get_children().specific(): one query instead of 2+, and
            # select_related avoids an extra query per header image (N+1).
            all_blogpages = (
                BlogPage.objects.child_of(self)
                .live()
                .public()
                .select_related("header_image")
                .order_by("-date")
            )
        else:
            all_blogpages = BlogPage.objects.none()

        paginator = Paginator(all_blogpages, self.posts_per_page)
        page_number = request.GET.get("page", 1)

        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            page_obj = paginator.page(1)

        context["page_obj"] = page_obj
        context["blogpages"] = page_obj.object_list
        context["paginator"] = paginator
        context["is_paginated"] = paginator.num_pages > 1
        return context


class BlogPageTag(TaggedItemBase):
    """Tags for blog posts."""

    content_object = ParentalKey(
        "BlogPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class BlogPage(Page):
    """Individual blog post page."""

    # Posts may only be created under the blog index, so their URLs are
    # always /blog/<slug>/ and they always appear in the index listing.
    parent_page_types = ["blog.BlogIndexPage"]

    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField(
        [
            ("rich_text", RichTextBlock()),
            ("image", ImageChooserBlock(template="blog/blocks/image_block.html")),
            ("video", EmbedBlock(help_text="Paste a YouTube or Vimeo URL")),
        ],
        blank=True,
    )
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Header image for the blog post",
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("date"),
                FieldPanel("tags"),
                FieldPanel("header_image"),
            ],
            heading="Blog post details",
        ),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]
