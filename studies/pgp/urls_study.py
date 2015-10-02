from django.conf.urls import url

from .views import DataRetrievalView
from ..views import StudyConnectionReturnRedirectView

urlpatterns = [
    url(r'^return/$', StudyConnectionReturnRedirectView.as_view(),
        name='study-connection-return'),

    url(r'^request-data-retrieval/$', DataRetrievalView.as_view(),
        name='request-data-retrieval'),
]
