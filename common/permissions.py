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
            assert False, ('TokenHasReadWriteScope requires the'
                           '`OAuth2Authentication` authentication '
                           'class to be used.')

        if hasattr(obj, 'user'):
            print 'token.user', token.user
            print 'obj.user', obj.user

            return token.user == obj.user
