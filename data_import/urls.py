from django.urls import re_path

from .views import DataFileDownloadView, RemovedDataView

app_name = 'data-management'

urlpatterns = [
    re_path(r'^datafile-download/(?P<pk>[0-9]+)/',
            DataFileDownloadView.as_view(),
            name='datafile-download'),
]
