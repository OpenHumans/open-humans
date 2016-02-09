from django.conf.urls import url

from data_import.views import DataRetrievalView


urlpatterns = [
    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source='american_gut'),
        name='request-data-retrieval'),
]
