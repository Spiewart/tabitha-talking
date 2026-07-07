from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model for Tabitha Talking.

    Admin-only — no public registration.
    """

    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    def get_full_name(self) -> str:
        """Used by the Wagtail admin (user listing, greetings).

        AbstractUser's version concatenates the removed first/last name
        fields, which renders as "None None".
        """
        return self.name or self.username

    def get_short_name(self) -> str:
        return self.name or self.username
