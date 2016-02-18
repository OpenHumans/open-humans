from django.conf.urls import url

from data_import.views import DataRetrievalView

from . import label
from .views import UploadView


urlpatterns = [
    url(r'^upload/$', UploadView.as_view(), name='upload'),

    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source=label),
        name='request-data-retrieval'),
]
