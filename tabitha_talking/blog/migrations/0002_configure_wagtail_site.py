"""Configure Wagtail Site root page for fresh databases.

Wagtail's initial migration creates a default "Welcome to your new Wagtail site!"
page and points the default Site to it. This migration removes that placeholder
and points the Site root to the actual Wagtail root page, so all child pages
created in the CMS are immediately routable.
"""

from django.db import migrations


def configure_site(apps, schema_editor):
    Site = apps.get_model("wagtailcore", "Site")
    Page = apps.get_model("wagtailcore", "Page")

    # The Wagtail root page (depth=1, invisible top-level node)
    root_page = Page.objects.filter(depth=1).first()
    if not root_page:
        return

    # Point the default Site to the actual root page FIRST
    # (Site.root_page has on_delete=CASCADE, so deleting the old root page
    # would cascade-delete the Site if we don't re-point it first)
    site = Site.objects.first()
    if site:
        site.root_page = root_page
        site.site_name = "Tabitha Talking"
        site.is_default_site = True
        site.save()
    else:
        # No Site exists — create one
        Site.objects.create(
            hostname="tabithatalking.com",
            port=80,
            site_name="Tabitha Talking",
            root_page=root_page,
            is_default_site=True,
        )

    # Now safe to delete the default "Welcome to your new Wagtail site!" page
    Page.objects.filter(depth=2, slug="home").delete()

    # Update root page's numchild after raw delete
    # (raw QuerySet.delete() bypasses treebeard's bookkeeping)
    root_page.numchild = Page.objects.filter(depth=2).count()
    root_page.save()


def reverse_configure_site(apps, schema_editor):
    # No-op: reversing would require recreating the Welcome page,
    # which isn't worth the complexity.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.RunPython(configure_site, reverse_configure_site),
    ]
