from django.contrib.auth.models import User
from restfw_composed_permissions.base import (BaseComposedPermission,
                                              BasePermissionComponent)
from restfw_composed_permissions.generic.components import AllowAll


class ObjectHasRequestUser(BasePermissionComponent):
    """
    The object's user matches the request's user.
    """
    def has_object_permission(self, permission, request, view, obj):
        if not request.user:
            return False

        if isinstance(obj, User):
            return request.user == obj

        if not hasattr(obj, 'user'):
            assert False, ('ObjectHasRequestUser used on an object with no '
                           'user field.')

        return request.user == obj.user


class ObjectHasTokenUser(BasePermissionComponent):
    """
    The object's user matches the token's user.
    """
    def has_object_permission(self, permission, request, view, obj):
        if not request.auth:
            return False

        if isinstance(obj, User):
            return request.auth.user == obj

        if not hasattr(obj, 'user'):
            assert False, ('ObjectHasTokenUser used on an object with no user '
                           'field.')

        if not hasattr(request.auth, 'scope'):
            assert False, ('ObjectHasTokenUser requires the'
                           '`OAuth2Authentication` authentication '
                           'class to be used.')

        return request.auth.user == obj.user


class ObjectHasTokenOrRequestUser(BaseComposedPermission):
    def global_permission_set(self):
        # QuerySet filtering enforces ownership
        return AllowAll()

    def object_permission_set(self):
        return (ObjectHasTokenUser() |
                ObjectHasRequestUser())
