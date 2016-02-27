from django.conf.urls import url

from activities.views import DisconnectView
from data_import.views import DataRetrievalView, FinalizeRetrievalView

from . import label


urlpatterns = [
    url(r'^finalize-import/$',
        FinalizeRetrievalView.as_view(source=label),
        name='finalize-import'),

    url(r'^disconnect/$',
        DisconnectView.as_view(source=label),
        name='disconnect'),

    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source=label),
        name='request-data-retrieval'),
]
