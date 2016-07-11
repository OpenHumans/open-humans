from django.conf.urls import url

from data_import.views import DataRetrievalView

from . import label
from .views import (DeleteVCFDataView, EditVCFDataView,
                    ManageVCFDataView, UploadVCFDataView)

urlpatterns = [
    url(r'^upload-file/$',
        UploadVCFDataView.as_view(),
        name='upload'),
    url(r'^file/(?P<vcf_data>[0-9]+)/$',
        EditVCFDataView.as_view(),
        name='file'),
    url(r'^file/$',
        EditVCFDataView.as_view(latest=True),
        name='latest-file'),
    url(r'^manage-files/$',
        ManageVCFDataView.as_view(),
        name='manage-files'),
    url(r'^delete-file/(?P<vcf_data>[0-9]+)/$',
        DeleteVCFDataView.as_view(),
        name='delete-file'),
    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source=label),
        name='request-data-retrieval'),
]
