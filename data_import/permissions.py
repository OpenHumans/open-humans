from django.conf import settings

from rest_framework.permissions import BasePermission


class LogAPIAccessAllowed(BasePermission):
    """
    Return True if the request is from OHLOG_PROJECT_ID.
    """

    def has_permission(self, request, view):
        if settings.OHLOG_PROJECT_ID:
            if request.auth.id == int(settings.OHLOG_PROJECT_ID):
                return True
        return False
