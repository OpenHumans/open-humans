"""
WSGI config for open_humans project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "open_humans.settings")

from django.core.cache.backends.memcached import BaseMemcachedCache
from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

# Fix django closing connection to MemCachier after every request (#11331)
BaseMemcachedCache.close = lambda self, **kwargs: None

application = DjangoWhiteNoise(get_wsgi_application())
