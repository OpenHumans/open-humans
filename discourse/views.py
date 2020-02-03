import base64
import hmac
import hashlib

from urllib.parse import parse_qs, unquote, urlencode

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic.base import View

from common.mixins import PrivateMixin


class SingleSignOn(PrivateMixin, View):
    def get(self, request):
        """
        Support Discourse single sign-on.
        """
        payload = request.GET.get("sso")
        signature = request.GET.get("sig")

        if None in [payload, signature]:
            return HttpResponseBadRequest(
                "No SSO payload or signature. Please "
                "contact support if this problem persists."
            )

        # Validate the payload
        try:
            payload = unquote(payload).encode("utf-8")
            decoded = base64.decodebytes(payload).decode("utf-8")

            assert "nonce" in decoded
            assert len(payload) > 0

        except AssertionError:
            return HttpResponseBadRequest(
                "Invalid payload. Please contact support if this problem persists."
            )

        key = settings.DISCOURSE_SSO_SECRET.encode("utf-8")
        h = hmac.new(key, payload, digestmod=hashlib.sha256)
        this_signature = h.hexdigest()

        if this_signature != signature:
            return HttpResponseBadRequest(
                "Invalid payload. Please contact support if this problem persists."
            )

        # Build the return payload
        qs = parse_qs(decoded)

        if not request.user.member.primary_email.verified:
            return HttpResponseBadRequest(
                "Please verify your Open Humans email address."
            )

        params = {
            "nonce": qs["nonce"][0],
            "name": request.user.member.name,
            "email": request.user.member.primary_email.email,
            "external_id": request.user.id,
            "username": request.user.username,
        }

        try:
            params["avatar_url"] = request.user.member.profile_image.url
            params["avatar_force_update"] = "true"
        except ValueError:
            pass

        return_payload = urlencode(params).encode("utf-8")
        b64_return_payload = base64.b64encode(return_payload)
        h = hmac.new(key, b64_return_payload, digestmod=hashlib.sha256)

        query_string = urlencode({"sso": b64_return_payload, "sig": h.hexdigest()})

        # Redirect back to Discourse
        url = "%s/session/sso_login" % settings.DISCOURSE_BASE_URL

        return HttpResponseRedirect("%s?%s" % (url, query_string))
