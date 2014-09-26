from django.conf.urls import include, patterns, url

from .american_gut import urls as american_gut_urls
from .flu_near_you import urls as flu_near_you_urls

urlpatterns = patterns(
    '',

    url(r'^american-gut/', include(american_gut_urls)),
    url(r'^flu-near-you/', include(flu_near_you_urls)),
)
