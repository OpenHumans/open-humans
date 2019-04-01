from django.urls import re_path

from .views import (
    DataFileDownloadView,
    DataTypesCreateView,
    DataTypesDetailView,
    DataTypesListView,
    DataTypesUpdateView,
)

app_name = "data-management"

urlpatterns = [
    re_path(
        r"^datafile-download/(?P<pk>[0-9]+)/",
        DataFileDownloadView.as_view(),
        name="datafile-download",
    ),
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
]
