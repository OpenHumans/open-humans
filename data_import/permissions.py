from rest_framework.permissions import BasePermission


class LogAPIAccessAllowed(BasePermission):
    """
    Return True if the request has a valid project token.
    """

    def has_permission(self, request, view):
        return request.auth.log_api_access
