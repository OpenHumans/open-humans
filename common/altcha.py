"""
ALTCHA proof-of-work CAPTCHA: a form field, its widget, and the view that
issues challenges.

The browser widget fetches a signed challenge, burns CPU finding a counter
whose derived key matches it, and submits the solution with the form. The
field verifies the signature and solution, and accepts each challenge once.
"""

import datetime

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from altcha import Payload, create_challenge, verify_solution

ALGORITHM = "PBKDF2/SHA-256"
# Key-derivation iterations per attempt; a browser needs about a second
COST = 5000
CHALLENGE_LIFETIME = datetime.timedelta(minutes=20)


def new_challenge():
    return create_challenge(
        algorithm=ALGORITHM,
        cost=COST,
        expires_at=datetime.datetime.now(datetime.timezone.utc) + CHALLENGE_LIFETIME,
        hmac_secret=settings.SECRET_KEY,
    )


@never_cache
@require_GET
def challenge_view(request):
    return JsonResponse(new_challenge().to_dict())


class AltchaWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return format_html(
            '<script async defer type="module" src="{}"></script>'
            '<altcha-widget challenge="{}" name="{}"></altcha-widget>',
            static("altcha/altcha.min.js"),
            reverse("altcha-challenge"),
            name,
        )


class AltchaField(forms.CharField):
    widget = AltchaWidget

    default_error_messages = {
        "required": "Please complete the verification.",
        "invalid": "Verification failed. Please try again.",
    }

    def __init__(self, **kwargs):
        kwargs.setdefault("label", "")
        super().__init__(**kwargs)

    def validate(self, value):
        super().validate(value)

        if not verify_solution(value, settings.SECRET_KEY).verified:
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        signature = Payload.from_base64(value).challenge.signature

        # cache.add only stores the key when it is absent, so a second
        # submission of the same solved challenge is rejected
        if not cache.add(
            "altcha-used-{}".format(signature),
            True,
            timeout=CHALLENGE_LIFETIME.total_seconds(),
        ):
            raise ValidationError(self.error_messages["invalid"], code="invalid")
