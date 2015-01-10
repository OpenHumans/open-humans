from django.conf.urls import include, patterns, url

from .american_gut import urls as american_gut_urls
from .go_viral import urls as go_viral_urls
# from .pgp import urls as pgp_urls

urlpatterns = patterns(
    '',

    url(r'^american-gut/', include(american_gut_urls)),
    url(r'^go-viral/', include(go_viral_urls)),
    # url(r'^pgp/', include(pgp_urls)),
)
