from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from common.permissions import ObjectHasTokenOrRequestUser
from common.viewset_mixins import SimpleCurrentUserMixin

from common.filter_backends import IsCurrentUserFilterBackend


class SimpleCurrentUserViewset(NestedViewSetMixin, SimpleCurrentUserMixin,
                               viewsets.ModelViewSet):
    filter_backends = (IsCurrentUserFilterBackend,)
    permission_classes = (ObjectHasTokenOrRequestUser,)
