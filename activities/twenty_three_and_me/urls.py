from django.conf.urls import patterns, url

from .views import (DataRetrievalView, ProfileIdCreateView,
                    TwentyThreeAndMeNamesJSON)


urlpatterns = patterns(
    '',

    url(r'^complete-import/$', ProfileIdCreateView.as_view(),
        name='complete-import'),

    url(r'^request-data-retrieval/$', DataRetrievalView.as_view(),
        name='request-data-retrieval'),

    url(r'^get-names/$', TwentyThreeAndMeNamesJSON.as_view(),
        name='get-names'),
)
