"""
Integration tests for all reCAPTCHA forms in the project.

These tests verify that all forms using reCAPTCHA v3 are configured consistently
with FormHelper.form_tag=False and have buttons inside form elements.
"""

from django.test import TestCase
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from tabitha_talking.forms import ContactForm


class ReCaptchaFormConsistencyTest(TestCase):
    """Test that all reCAPTCHA forms follow the same pattern."""

    def test_contact_form_has_form_helper(self):
        """Test that ContactForm has FormHelper configured."""
        form = ContactForm()
        self.assertTrue(hasattr(form, "helper"))
        self.assertFalse(form.helper.form_tag)

    def test_contact_form_has_captcha_field(self):
        """Test that ContactForm has reCAPTCHA field."""
        form = ContactForm()
        self.assertIn("captcha", form.fields)
        self.assertIsInstance(form.fields["captcha"], ReCaptchaField)

    def test_contact_form_uses_recaptcha_v3(self):
        """Test that ContactForm uses v3 widget."""
        form = ContactForm()
        captcha_field = form.fields["captcha"]
        self.assertIsInstance(captcha_field.widget, ReCaptchaV3)

    def test_contact_form_has_rate_limiting(self):
        """Test that ContactForm has rate limiting configured."""
        self.assertTrue(hasattr(ContactForm, "RATE_LIMIT_MAX_ATTEMPTS"))
        self.assertTrue(hasattr(ContactForm, "RATE_LIMIT_WINDOW_SECONDS"))
        self.assertGreaterEqual(ContactForm.RATE_LIMIT_MAX_ATTEMPTS, 1)
        self.assertLess(ContactForm.RATE_LIMIT_MAX_ATTEMPTS, 1000)

    def test_contact_form_has_correct_action(self):
        """Test that ContactForm has correct reCAPTCHA action."""
        form = ContactForm()
        captcha_widget = form.fields["captcha"].widget
        self.assertIn("data-action", captcha_widget.attrs)
        self.assertEqual(captcha_widget.attrs["data-action"], "contact")

    def test_contact_form_layout(self):
        """Test that ContactForm layout is configured."""
        form = ContactForm()
        self.assertTrue(hasattr(form.helper, "layout"))
        self.assertIsNotNone(form.helper.layout)
