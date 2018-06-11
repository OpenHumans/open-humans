from django.conf.urls import url

from .views import (DataFileDownloadView, DataFileListView,
                    ProcessingParametersView, TaskUpdateView)

urlpatterns = [
    url(r'^task-update/', TaskUpdateView.as_view(), name='task-update'),

    url(r'^data-files/', DataFileListView.as_view(), name='data-files'),

    url(r'^parameters/',
        ProcessingParametersView.as_view(),
        name='parameters'),

    url(r'^datafile-download/(?P<pk>[0-9]+)/',
        DataFileDownloadView.as_view(),
        name='datafile-download'),
]
