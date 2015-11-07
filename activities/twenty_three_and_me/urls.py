from django.conf.urls import patterns, url

from .views import DataRetrievalView, UploadView


urlpatterns = patterns(
    '',

    url(r'^upload/$', UploadView.as_view(), name='upload'),

    url(r'^request-data-retrieval/$', DataRetrievalView.as_view(),
        name='request-data-retrieval'),
)
