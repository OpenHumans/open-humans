from django.conf.urls import include, patterns, url

from . import american_gut
from . import flu_near_you

urlpatterns = patterns(
    '',

    url(r'^american-gut/', include(american_gut.urls)),
    url(r'^flu-near-you/', include(flu_near_you.urls)),
)
