from django.conf.urls import patterns, url

from .views import DataFileDownloadView, TaskUpdateView

urlpatterns = patterns(
    '',

    url(r'^task-update/', TaskUpdateView.as_view(), name='task-update'),
    url(r'^datafile-download/(?P<pk1>[0-9]+)/(?P<pk2>[0-9]+)/',
        DataFileDownloadView.as_view(), name='datafile-download'),
)
