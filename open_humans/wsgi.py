"""
WSGI config for open_humans project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import logging
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'open_humans.settings')

from django.conf import settings
from django.core.cache.backends.memcached import BaseMemcachedCache
from django.core.wsgi import get_wsgi_application

from whitenoise.django import DjangoWhiteNoise

logger = logging.getLogger(__name__)

logger.info('WSGI application starting')

logger.info('DEBUG: %s', settings.DEBUG)
logger.info('OAUTH2_DEBUG: %s', settings.OAUTH2_DEBUG)
logger.info('LOG_EVERYTHING: %s', settings.LOG_EVERYTHING)

# Fix django closing connection to MemCachier after every request (#11331)
BaseMemcachedCache.close = lambda self, **kwargs: None

application = DjangoWhiteNoise(get_wsgi_application())
