from django.conf.urls import include, url

from .data_selfie import urls as data_selfie_urls
from .runkeeper import urls as runkeeper_urls
from .twenty_three_and_me import urls as twenty_three_and_me_urls

urlpatterns = [
    # Activities
    url(r'^23andme/', include(twenty_three_and_me_urls, namespace='23andme')),
    url(r'^data-selfie/', include(data_selfie_urls, namespace='data-selfie')),
    url(r'^runkeeper/', include(runkeeper_urls, namespace='runkeeper')),
]
