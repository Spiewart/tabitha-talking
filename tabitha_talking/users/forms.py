"""Wagtail admin user forms for the custom User model.

The project's User model (cookiecutter-django pattern) removes
first_name/last_name in favour of a single ``name`` field. Wagtail's
stock user forms declare First/Last name as required inputs and assign
them to attributes that are not database fields, so edits silently
vanish. These subclasses drop those fields and expose ``name``.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from wagtail.users.forms import UserCreationForm as WagtailUserCreationForm
from wagtail.users.forms import UserEditForm as WagtailUserEditForm

User = get_user_model()


class UserEditForm(WagtailUserEditForm):
    # Setting inherited declared fields to None removes them.
    first_name = None
    last_name = None
    name = forms.CharField(required=False, label=_("Name"))

    class Meta(WagtailUserEditForm.Meta):
        model = User
        fields = {User.USERNAME_FIELD, "name", "email", "is_active"} | {
            "is_superuser",
            "groups",
        }


class UserCreationForm(WagtailUserCreationForm):
    first_name = None
    last_name = None
    name = forms.CharField(required=False, label=_("Name"))

    class Meta(WagtailUserCreationForm.Meta):
        model = User
        fields = {User.USERNAME_FIELD, "name", "email"} | {
            "is_superuser",
            "groups",
        }
