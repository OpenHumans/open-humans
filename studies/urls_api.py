"""
URLs used for performing API interactions involving the studies.
"""
from django.conf.urls import include, patterns, url

from .american_gut import urls_api as american_gut_urls_api
from .go_viral import urls_api as go_viral_urls_api
from .pgp import urls_api as pgp_urls_api
from .wildlife import urls_api as wildlife_urls_api

urlpatterns = patterns(
    '',

    url(r'^american-gut/', include(american_gut_urls_api)),
    url(r'^go-viral/', include(go_viral_urls_api)),
    url(r'^pgp/', include(pgp_urls_api)),
    url(r'^wildlife/', include(wildlife_urls_api)),
)
