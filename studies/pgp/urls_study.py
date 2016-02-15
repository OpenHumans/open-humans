from django.conf.urls import url

from data_import.views import DataRetrievalView


urlpatterns = [
    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source='pgp'),
        name='request-data-retrieval'),
]
