from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from .views import DataRetrievalView, TwentyThreeAndMeNamesJSON


urlpatterns = patterns(
    '',
    url(r'^complete-import/$',
        TemplateView.as_view(
            template_name='twenty_three_and_me/complete-import-23andme.html'),
        name='complete-import'),
    url(r'^request-data-retrieval-task/$', DataRetrievalView.as_view(),
        name='request-data-retrieval-task'),

    url(r'^get-names/$', TwentyThreeAndMeNamesJSON.as_view(),
        name='get-names'),
)
