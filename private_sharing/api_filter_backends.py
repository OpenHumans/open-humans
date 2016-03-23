from rest_framework.filters import BaseFilterBackend


class ProjectFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(project=request.auth)
