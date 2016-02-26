from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from activities.views import DisconnectView
from data_import.views import DataRetrievalView, FinalizeRetrievalView

from . import label
from .views import DeauthorizeView


urlpatterns = [
    url(r'^finalize-import/$',
        FinalizeRetrievalView.as_view(source=label),
        name='finalize-import'),

    url(r'^deauthorize/$',
        csrf_exempt(DeauthorizeView.as_view()),
        name='deauthorize'),

    url(r'^disconnect/$',
        DisconnectView.as_view(source=label),
        name='disconnect'),

    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source=label),
        name='request-data-retrieval'),
]
