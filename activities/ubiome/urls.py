from django.conf.urls import url

from data_import.views import DataRetrievalView

from . import label
from .views import (CreateUBiomeSampleView, DeleteUBiomeSampleView,
                    ManageUBiomeSamplesView, UploadUBiomeSequenceView)


urlpatterns = [
    url(r'^sample-info/$',
        CreateUBiomeSampleView.as_view(),
        name='sample-info'),
    url(r'^sample-upload/(?P<sample>[0-9]+)/$',
        UploadUBiomeSequenceView.as_view(),
        name='sample-upload'),
    url(r'^manage-samples/$',
        ManageUBiomeSamplesView.as_view(),
        name='manage-samples'),
    url(r'^delete-sample/(?P<sample>[0-9]+)/$',
        DeleteUBiomeSampleView.as_view(),
        name='delete-sample'),
    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source=label),
        name='request-data-retrieval'),
]
