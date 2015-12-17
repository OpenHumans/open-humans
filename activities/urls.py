from django.conf.urls import include, url

from .runkeeper import urls as runkeeper_urls
from .twenty_three_and_me import urls as twenty_three_and_me_urls

urlpatterns = [
    # Activities
    url(r'^23andme/', include(twenty_three_and_me_urls, namespace='23andme')),
    url(r'^runkeeper/', include(runkeeper_urls, namespace='runkeeper')),
]
