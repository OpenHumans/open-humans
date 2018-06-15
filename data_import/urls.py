from django.conf.urls import url

from .views import DataFileDownloadView

urlpatterns = [
    url(r'^datafile-download/(?P<pk>[0-9]+)/',
        DataFileDownloadView.as_view(),
        name='datafile-download'),
]
