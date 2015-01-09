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
