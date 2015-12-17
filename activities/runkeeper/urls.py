from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import (DataRetrievalView, DeauthorizeView, DisconnectView,
                    FinalizeImportView)


urlpatterns = [
    url(r'^finalize-import/$',
        FinalizeImportView.as_view(),
        name='finalize-import'),

    url(r'^deauthorize/$',
        csrf_exempt(DeauthorizeView.as_view()),
        name='deauthorize'),

    url(r'^disconnect/$',
        DisconnectView.as_view(),
        name='disconnect'),

    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(),
        name='request-data-retrieval'),
]
