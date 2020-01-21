import base64
import hmac
import hashlib
import urllib

from urlparse import parse_qs

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings


@login_required
def single_sign_on(request):
    """
    Support Discourse single sign-on.
    """
    payload = request.GET.get("sso")
    signature = request.GET.get("sig")

    if None in [payload, signature]:
        return HttpResponseBadRequest(
            "No SSO payload or signature. Please "
            "contact support if this problem "
            "persists."
        )

    # Validate the payload
    try:
        payload = urllib.unquote(payload)
        decoded = base64.decodestring(payload)

        assert "nonce" in decoded
        assert len(payload) > 0
    except AssertionError:
        return HttpResponseBadRequest(
            "Invalid payload. Please contact " "support if this problem persists."
        )

    key = str(settings.DISCOURSE_SSO_SECRET)
    h = hmac.new(key, payload, digestmod=hashlib.sha256)
    this_signature = h.hexdigest()

    if this_signature != signature:
        return HttpResponseBadRequest(
            "Invalid payload. Please contact " "support if this problem persists."
        )

    # Build the return payload
    qs = parse_qs(decoded)

    if not request.user.member.primary_email.verified:
        return HttpResponseBadRequest(
            "Please verify your Open Humans email " "address."
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

    return_payload = base64.encodestring(urllib.urlencode(params))
    h = hmac.new(key, return_payload, digestmod=hashlib.sha256)

    query_string = urllib.urlencode({"sso": return_payload, "sig": h.hexdigest()})

    # Redirect back to Discourse
    url = "%s/session/sso_login" % settings.DISCOURSE_BASE_URL

    return HttpResponseRedirect("%s?%s" % (url, query_string))
