from django.conf.urls import include, patterns, url

from .twenty_three_and_me import urls as twenty_three_and_me_urls

urlpatterns = patterns(
    '',

    # Activities
    url(r'^23andme/', include(twenty_three_and_me_urls, namespace='23andme')),
)
