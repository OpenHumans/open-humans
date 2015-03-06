from django.conf.urls import url

from .views import DataRetrievalView

urlpatterns = [
    url(r'^request-data-retrieval/$', DataRetrievalView.as_view(),
        name='request-data-retrieval'),
]
