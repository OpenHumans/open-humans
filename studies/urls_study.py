"""
URLs used by Members for interacting with a study.
"""
from django.conf.urls import include, patterns, url

from .american_gut import urls_study as american_gut_urls_study
from .go_viral import urls_study as go_viral_urls_study
from .pgp import urls_study as pgp_urls_study

from .views import StudyAuthorizationView, StudyConnectionView

urlpatterns = patterns(
    '',

    url(r'^american-gut/',
        include(american_gut_urls_study, namespace='american-gut')),
    url(r'^go-viral/', include(go_viral_urls_study, namespace='go-viral')),
    url(r'^pgp/', include(pgp_urls_study, namespace='pgp')),

    url(r'^connect/(?P<slug>[a-z0-9-]+)/$', StudyConnectionView.as_view()),

    # Add a simple OAuth2 authorize step tailored to studies
    url(r'^authorize/$', StudyAuthorizationView.as_view(), name='authorize'),
)
