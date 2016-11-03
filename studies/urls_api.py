"""
URLs used for performing API interactions involving the studies.
"""
from django.conf.urls import include, url

from .american_gut import urls_api as american_gut_urls_api
from .pgp import urls_api as pgp_urls_api
from .wildlife import urls_api as wildlife_urls_api

urlpatterns = [
    url(r'^american-gut/', include(american_gut_urls_api)),
    url(r'^pgp/', include(pgp_urls_api)),
    url(r'^wildlife/', include(wildlife_urls_api)),
]
