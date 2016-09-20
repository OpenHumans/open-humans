from django.conf.urls import url

from data_import.views import DataRetrievalView

from . import label, views


urlpatterns = [
    url(r'^manage/$', views.DataSelfieView.as_view(), name='manage'),

    url(r'^upload/$', views.UploadView.as_view(), name='upload'),

    url(r'^request-data-retrieval/$',
        DataRetrievalView.as_view(source=label),
        name='request-data-retrieval'),

    url(r'^acknowledge/$',
        views.DataSelfieAcknowledgeView.as_view(),
        name='acknowledge'),

    url(r'^delete/(?P<data_file>[0-9]+)/$',
        views.DataSelfieFileDeleteView.as_view(),
        name='delete-file'),

    url(r'^(?P<data_file>[0-9]+)/$',
        views.DataSelfieUpdateView.as_view(),
        name='edit-file'),
]
