from django.urls import path, re_path

from .views import (
    AWSDataFileAccessLogView,
    DataFileDownloadView,
    NewDataFileAccessLogView,
)

app_name = "data-management"

urlpatterns = [
    re_path(
        r"^datafile-download/(?P<pk>[0-9]+)/",
        DataFileDownloadView.as_view(),
        name="datafile-download",
    ),
    # Custom API endpoints for OHLOG_PROJECT_ID
    path(
        "awsdatafileaccesslog/",
        AWSDataFileAccessLogView.as_view(),
        name="awsdatafileaccesslog",
    ),
    path(
        "newdatafileaccesslog/",
        NewDataFileAccessLogView.as_view(),
        name="newdatafileaccesslog",
    ),
]
