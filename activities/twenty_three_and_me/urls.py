from django.conf.urls import url

from data_import.views import DataRetrievalView

from .views import UploadView


urlpatterns = [
    url(r'^upload/$', UploadView.as_view(), name='upload'),

    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source='twenty_three_and_me'),
        name='request-data-retrieval'),
]
