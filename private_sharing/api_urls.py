from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from .api_views import ProjectDataView, ProjectMemberDataView

urlpatterns = [
    url(r'^project/$', ProjectDataView.as_view()),
    url(r'^project/members/$', ProjectMemberDataView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
