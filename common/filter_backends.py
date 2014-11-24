from django.contrib.auth.models import User
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.filters import BaseFilterBackend


class IsCurrentUserFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        if not (request.user.is_authenticated() or request.auth):
            raise NotAuthenticated

        if not hasattr(view, 'get_parents_query_dict'):
            return queryset.filter(user=request.user)

        query_dict = view.get_parents_query_dict()

        if not query_dict:
            if queryset.model == User:
                return queryset.filter(pk=request.user.pk)
            else:
                return queryset.filter(user=request.user)

        args = {}

        for key, value in query_dict.iteritems():
            parent_model = getattr(queryset.model, key)

            parent_user = (parent_model.field.related_field.model.objects
                           .get(pk=value).user)

            if request.user != parent_user:
                raise PermissionDenied

            args[key + '__user_id'] = request.user.pk

        return queryset.filter(**args)
