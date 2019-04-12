from django.urls import path, re_path

from .views import (
    AWSDataFileAccessLogView,
    DataFileDownloadView,
    DataTypesCreateView,
    DataTypesDetailView,
    DataTypesListView,
    DataTypesUpdateView,
    NewDataFileAccessLogView,
)

app_name = "data-management"

urlpatterns = [
    re_path(
        r"^datafile-download/(?P<pk>[0-9]+)/",
        DataFileDownloadView.as_view(),
        name="datafile-download",
    ),
    # DataType endpoints
    re_path(
        r"^datatypes/create/", DataTypesCreateView.as_view(), name="datatypes-create"
    ),
    re_path(
        r"^datatypes/update/(?P<pk>[\w-]+)$",
        DataTypesUpdateView.as_view(),
        name="datatypes-update",
    ),
    re_path(
        r"^datatypes/(?P<pk>[\w-]+)$",
        DataTypesDetailView.as_view(),
        name="datatypes-detail",
    ),
    re_path(r"^datatypes/", DataTypesListView.as_view(), name="datatypes-list"),
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
