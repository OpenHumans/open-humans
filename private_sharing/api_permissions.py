from rest_framework.permissions import BasePermission


class HasValidProjectToken(BasePermission):
    """
    Return True if the request has a valid project token.
    """

    def has_permission(self, request, view):
        return bool(request.auth)


class CanProjectAccessData(BasePermission):
    """
    Return true if any of the following conditions are met:
    On Site project
    Approved OAuth2 project
    UnApproved OAuth2 project with diyexperiment=False
    """

    def has_permission(self, request, view):
        if hasattr(request.auth, "onsitedatarequestproject"):
            return True
        if request.auth.approved == True:
            return True
        if request.auth.oauth2datarequestproject.diyexperiment == False:
            return True
        return False
