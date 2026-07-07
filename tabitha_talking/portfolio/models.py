from django.core.validators import FileExtensionValidator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import InlinePanel
from wagtail.admin.panels import MultiFieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import RichTextField
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable
from wagtail.models import Page
from wagtail.search import index


class DemoCategory(models.TextChoices):
    COMMERCIAL = "commercial", "Commercial"
    NARRATION = "narration", "Narration"
    CHARACTER = "character", "Animation / Character"
    AUDIOBOOK = "audiobook", "Audiobook"
    ELEARNING = "elearning", "E-Learning"
    PROMO = "promo", "Promo"
    OTHER = "other", "Other"


class PortfolioIndexPage(Page):
    """Main portfolio page listing demo reels and media."""

    intro = RichTextField(blank=True)

    # Only demo reels may live under the portfolio index, and there
    # should be exactly one portfolio index (served at /portfolio/).
    subpage_types = ["portfolio.DemoReelPage"]
    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("headshots", label="Headshots"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        if self.pk:
            # Query the concrete model directly: cheaper than
            # get_children().specific() and lets us order in one query.
            demos = (
                DemoReelPage.objects.child_of(self).live().public().order_by("title")
            )
            headshots = self.headshots.select_related("image")
        else:
            demos = DemoReelPage.objects.none()
            headshots = []
        # Group demos by category
        demos_by_category = {}
        for demo in demos:
            category_label = demo.get_category_display()
            demos_by_category.setdefault(category_label, []).append(demo)
        context["demos_by_category"] = demos_by_category
        context["all_demos"] = demos
        context["headshots"] = headshots
        return context


class PortfolioHeadshot(Orderable):
    """Headshot images for the portfolio page."""

    page = ParentalKey(
        PortfolioIndexPage,
        on_delete=models.CASCADE,
        related_name="headshots",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


class DemoReelPage(Page):
    """Individual demo reel page with audio player."""

    category = models.CharField(
        max_length=20,
        choices=DemoCategory,
        default=DemoCategory.COMMERCIAL,
    )
    audio_file = models.FileField(
        upload_to="demos/",
        validators=[
            FileExtensionValidator(allowed_extensions=["mp3", "wav", "ogg"]),
        ],
        help_text="Upload an audio file (MP3, WAV, or OGG). Max 50 MB.",
    )
    description = RichTextField(blank=True)
    duration = models.CharField(
        max_length=10,
        blank=True,
        help_text='Duration display (e.g., "1:30")',
    )
    transcript = RichTextField(
        blank=True,
        help_text="Optional transcript of the demo reel.",
    )

    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.FilterField("category"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("audio_file"),
                FieldPanel("duration"),
            ],
            heading="Demo details",
        ),
        FieldPanel("description"),
        FieldPanel("transcript"),
    ]

    parent_page_types = ["portfolio.PortfolioIndexPage"]


class AboutPage(Page):
    """About page with bio, photo, and credentials."""

    # A site needs only one About page (linked in the navbar at /about/).
    max_count = 1

    profile_photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Profile photo",
    )
    body = StreamField(
        [
            ("rich_text", RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("video", EmbedBlock(help_text="Paste a YouTube or Vimeo URL")),
        ],
        blank=True,
    )
    credentials = RichTextField(
        blank=True,
        help_text="Training, certifications, and credentials.",
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.SearchField("credentials"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("profile_photo"),
        FieldPanel("body"),
        FieldPanel("credentials"),
    ]
