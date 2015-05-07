from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from .views import DataRetrievalView


urlpatterns = patterns(
    '',

    url(r'^complete-import/$',
        TemplateView.as_view(
            template_name="runkeeper/complete-import-runkeeper.html"),
        name='complete-import'),

    url(r'^request-data-retrieval/$', DataRetrievalView.as_view(),
        name='request-data-retrieval'),
)
