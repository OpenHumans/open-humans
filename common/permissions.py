from rest_framework.permissions import BasePermission


class ObjectHasTokenUser(BasePermission):
    """
    The object's user matches the token's user.
    """
    def has_object_permission(self, request, view, obj):
        token = request.auth

        if not token:
            return False

        if not hasattr(token, 'scope'):
            assert False, ('ObjectHasTokenUser requires the'
                           '`OAuth2Authentication` authentication '
                           'class to be used.')

        if hasattr(obj, 'user'):
            return token.user == obj.user
