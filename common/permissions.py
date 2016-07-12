from django.conf import settings

from rest_framework.permissions import BasePermission


class HasValidToken(BasePermission):
    """
    The request has a valid token
    """

    def has_permission(self, request, view):
        if not request.auth:
            return False

        if not hasattr(request.auth, 'scope'):
            assert False, ('ObjectHasTokenUser requires the'
                           '`OAuth2Authentication` authentication '
                           'class to be used.')

        return True


class HasPreSharedKey(BasePermission):
    """
    The request contains the pre-shared key as a querystring parameter.
    """

    def has_permission(self, request, view):
        return request.query_params.get('key') == settings.PRE_SHARED_KEY
