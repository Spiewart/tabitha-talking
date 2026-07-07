# Django Forms with ReCAPTCHA v3 and Crispy Forms

## Overview

This document explains how to properly integrate Django forms with `django-recaptcha` v3 widget and `crispy-forms` to ensure form submissions work correctly.

## The Problem

When using `django-recaptcha` with the `ReCaptchaV3` widget alongside `crispy-forms`, a common issue occurs where form submissions fail silently:

1. **Button clicks don't trigger submit**: Clicking the submit button produces no console errors and no network requests
2. **Form doesn't respond**: The page appears frozen, nothing happens

### Root Cause

The issue stems from how `crispy-forms` renders forms:

- **`{% crispy form %}`** renders a **complete** `<form>` element including opening `<form>` and closing `</form>` tags
- If you place a submit button **after** `{% crispy form %}`, the button is rendered **outside** the form element
- The ReCAPTCHA v3 widget attaches a submit event listener to the form element
- Submit buttons outside the form don't trigger the form's submit event
- **Result**: Clicking the button does nothing

## The Solution

Use `FormHelper` with `form_tag=False` to prevent crispy-forms from rendering `<form>` tags, then manually add them in the template with the button inside.

### Implementation

**Form (forms.py):**
```python
from crispy_forms.helper import FormHelper
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

class ContactForm(Form):
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={"data-action": "contact"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Critical setting
```

**Template:**
```django
{% load crispy_forms_tags %}

{{ form.media }}  {# CRITICAL: Renders reCAPTCHA widget JavaScript #}
<form method="post" action="{% url 'contact' %}">
  {% csrf_token %}
  {% crispy form %}  {# Renders only fields, no <form> tags #}
  <button type="submit" class="btn btn-primary">Send Message</button>
</form>
```

**Key Elements:**

1. **`{{ form.media }}`** -- loads the reCAPTCHA JavaScript. Without this, the widget won't initialize.
2. **Manual `<form>` tags** -- you control the form wrapper.
3. **`{% csrf_token %}`** -- required for Django form submission security.
4. **`{% crispy form %}`** -- because `form_tag=False`, renders only fields.
5. **Submit button inside `<form>`** -- this is the critical fix.

## Forms Using ReCAPTCHA

| Form | Location | Template |
|------|----------|----------|
| ContactForm | `tabitha_talking/forms.py` | `templates/pages/contact.html` |

## Verification

Open browser console and run:

```javascript
const form = document.querySelector('form');
const button = document.querySelector('button[type="submit"]');
console.log(form.contains(button));  // Should return true
```

## References

- [django-recaptcha Documentation](https://github.com/torchbox/django-recaptcha)
- [crispy-forms FormHelper](https://django-crispy-forms.readthedocs.io/en/latest/form_helper.html)
- [Google reCAPTCHA v3](https://developers.google.com/recaptcha/docs/v3)
