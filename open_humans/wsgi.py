"""
WSGI config for open_humans project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import logging
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'open_humans.settings')

# pylint: disable=wrong-import-position
from django.conf import settings  # noqa
from django.core.cache.backends.memcached import BaseMemcachedCache  # noqa
from django.core.wsgi import get_wsgi_application  # noqa

logger = logging.getLogger(__name__)

logger.info('WSGI application starting')

logger.info('DEBUG: %s', settings.DEBUG)
logger.info('OAUTH2_DEBUG: %s', settings.OAUTH2_DEBUG)
logger.info('LOG_EVERYTHING: %s', settings.LOG_EVERYTHING)

# Fix django closing connection to MemCachier after every request (#11331)
BaseMemcachedCache.close = lambda self, **kwargs: None

application = get_wsgi_application()
