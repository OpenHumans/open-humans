from django.conf.urls import url

from data_import.views import DataRetrievalView

from ..views import StudyHomeView
from . import label


urlpatterns = [
    url(r'', StudyHomeView.as_view(source=label)),

    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source=label),
        name='request-data-retrieval'),
]
