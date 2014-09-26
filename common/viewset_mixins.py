from provider.oauth2.models import AccessToken

from rest_framework.exceptions import NotAuthenticated
from rest_framework_extensions.utils import compose_parent_pk_kwarg_name


class UserPkMixin(object):
    def get_user_pk(self, request):
        if request.user.is_authenticated():
            return request.user.pk
        elif 'access_token' in request.GET:
            return AccessToken.objects.get(
                token=request.GET['access_token']).user.pk
        elif 'HTTP_AUTHORIZATION' in request.META:
            return AccessToken.objects.get(
                token=request.META['HTTP_AUTHORIZATION'].split(' ')[1]).user.pk

        # XXX handle_exception relies on self.request but it gets set in
        # super().dispatch; we set it here as a workaround.
        self.request = request
        self.handle_exception(NotAuthenticated())


class NestedCurrentUserMixin(UserPkMixin):
    def dispatch(self, request, *args, **kwargs):
        kwarg_name = compose_parent_pk_kwarg_name(self.parent_attribute)

        if kwargs.get(kwarg_name) == 'current':
            kwargs[kwarg_name] = self.get_user_pk(request)

        return super(NestedCurrentUserMixin, self).dispatch(request, *args,
                                                            **kwargs)

    def pre_save(self, obj):
        kwarg_name = compose_parent_pk_kwarg_name(self.parent_attribute)

        parent_pk = self.kwargs[kwarg_name]

        setattr(obj, self.parent_attribute + '_id', parent_pk)


class SimpleCurrentUserMixin(UserPkMixin):
    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'current':
            kwargs['pk'] = self.get_user_pk(request)

        return super(SimpleCurrentUserMixin, self).dispatch(request, *args,
                                                            **kwargs)
