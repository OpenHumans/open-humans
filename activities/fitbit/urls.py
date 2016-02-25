from django.conf.urls import url

from data_import.views import DataRetrievalView

from . import label
from .views import DisconnectView, FinalizeImportView


urlpatterns = [
    url(r'^finalize-import/$',
        FinalizeImportView.as_view(),
        name='finalize-import'),

    url(r'^disconnect/$',
        DisconnectView.as_view(),
        name='disconnect'),

    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source=label),
        name='request-data-retrieval'),
]
