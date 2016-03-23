from rest_framework.permissions import BasePermission


class HasValidProjectToken(BasePermission):
    """
    Return True if the request has a valid project token.
    """

    def has_permission(self, request, view):
        return bool(request.auth)
