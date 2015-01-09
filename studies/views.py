from django.shortcuts import get_object_or_404

from rest_framework.generics import (ListCreateAPIView, RetrieveAPIView)
from rest_framework.mixins import DestroyModelMixin

# from common.permissions import ObjectHasTokenUser
from common.permissions import HasValidToken


class UserDataMixin(object):
    def get_user_data(self):
        """
        A helper function to retrieve the given study's UserData model that
        corresponds to the request user.
        """
        return self.user_data_model.objects.get(user=self.request.user)

    def get_user_data_queryset(self):
        """
        A helper function to retrieve the given study's UserData model as a
        pre-filtered queryset that corresponds to the request user.
        """
        return self.user_data_model.objects.filter(user=self.request.user)

    def get_object(self):
        """
        We don't use lookup fields because the only data accessible for each
        access token is that user's own data.
        """
        obj = get_object_or_404(self.get_queryset())

        self.check_object_permissions(self.request, obj)

        return obj


class StudyDetailView(UserDataMixin, RetrieveAPIView):
    permission_classes = (HasValidToken,)


class StudyListView(UserDataMixin, DestroyModelMixin, ListCreateAPIView):
    permission_classes = (HasValidToken,)
