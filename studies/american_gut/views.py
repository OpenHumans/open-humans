from rest_framework import permissions, viewsets

from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_extensions.utils import compose_parent_pk_kwarg_name

from common.permissions import ObjectHasTokenUser

from provider.oauth2.models import AccessToken

from .models import Barcode, UserData
from .serializers import BarcodeSerializer, UserDataSerializer

OAUTH2_PERMISSIONS = (permissions.TokenHasReadWriteScope, ObjectHasTokenUser)


def get_user_pk(request):
    if request.user.is_authenticated():
        return request.user.pk
    elif 'access_token' in request.GET:
        token = AccessToken.objects.get(token=request.GET['access_token'])

        return token.user.pk

    return None


class BarcodeViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Barcode
    serializer_class = BarcodeSerializer
    permission_classes = OAUTH2_PERMISSIONS

    def dispatch(self, request, *args, **kwargs):
        # XXX: No idea if this is the correct way to do this but it works!
        kwarg_name = compose_parent_pk_kwarg_name('user_data')

        if kwargs.get(kwarg_name) == 'current':
            kwargs[kwarg_name] = get_user_pk(request)

        return super(BarcodeViewSet, self).dispatch(request, *args, **kwargs)

    def pre_save(self, barcode):
        # XXX: No idea if this is the correct way to do this but it works!
        user_data_pk = self.kwargs[compose_parent_pk_kwarg_name('user_data')]

        barcode.user_data_id = user_data_pk


class UserDataViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = UserData.objects.all()
    serializer_class = UserDataSerializer
    permission_classes = OAUTH2_PERMISSIONS

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'current':
            kwargs['pk'] = get_user_pk(request)

        return super(UserDataViewSet, self).dispatch(request, *args, **kwargs)
