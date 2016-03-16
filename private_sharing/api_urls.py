from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from .api_views import ProjectDataView

urlpatterns = [
    url(r'^project-data/$', ProjectDataView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
