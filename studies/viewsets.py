from rest_framework import viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin

from common.permissions import ObjectHasTokenOrRequestUser
from common.viewset_mixins import (SimpleCurrentUserMixin,
                                   NestedCurrentUserMixin)

from common.filter_backends import IsCurrentUserFilterBackend


class NestedStudyViewset(NestedViewSetMixin, NestedCurrentUserMixin,
                         viewsets.ModelViewSet):
    filter_backends = (IsCurrentUserFilterBackend,)
    permission_classes = (ObjectHasTokenOrRequestUser,)


class StudyViewset(NestedViewSetMixin, SimpleCurrentUserMixin,
                   viewsets.ModelViewSet):
    filter_backends = (IsCurrentUserFilterBackend,)
    permission_classes = (ObjectHasTokenOrRequestUser,)
