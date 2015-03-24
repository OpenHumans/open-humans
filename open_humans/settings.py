"""
Django settings for open_humans project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import logging
import os
import sys

from distutils import util  # pylint: disable=no-name-in-module

import dj_database_url

from .utilities import apply_env, get_env


def to_bool(env, default='false'):
    """
    Convert a string to a bool.
    """
    return bool(util.strtobool(os.getenv(env, default)))


class FakeSite(object):
    """
    A duck-typing class to fool things that use django.contrib.sites.
    """
    name = 'Open Humans'

    def __init__(self, domain):
        self.domain = domain

    def __unicode__(self):
        return self.name

# Apply the env in the .env file
apply_env(get_env())

from django.conf import global_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PORT = os.getenv('PORT', 8000)

ENV = os.getenv('ENV', 'development')
DOMAIN = os.getenv('DOMAIN', 'localhost:{}'.format(PORT))

if ENV == 'staging' or ENV == 'production':
    # For email template URLs
    DEFAULT_HTTP_PROTOCOL = 'https'

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = to_bool('DEBUG')
OAUTH2_DEBUG = to_bool('OAUTH2_DEBUG')

TEMPLATE_DEBUG = DEBUG

LOG_EVERYTHING = to_bool('LOG_EVERYTHING')

console_at_info = {
    'handlers': ['console'],
    'level': 'INFO',
}

if LOG_EVERYTHING:
    LOGGING = {
        'disable_existing_loggers': False,
        'version': 1,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'django.db': {
                # django also has database level logging
            },
        },
    }
else:
    LOGGING = {
        'disable_existing_loggers': False,
        'version': 1,
        'formatters': {
            'open-humans': {
                '()': 'open_humans.formatters.LocalFormat',
                'format': '%(levelname)s %(context)s %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'open-humans'
            },
        },
        'loggers': {
            'django.request': console_at_info,
            # Log our modules at INFO
            'activities': console_at_info,
            'common': console_at_info,
            'data_import': console_at_info,
            'open_humans': console_at_info,
            'public_data': console_at_info,
            'studies': console_at_info,
        }
    }


if OAUTH2_DEBUG:
    oauth_log = logging.getLogger('oauthlib')

    oauth_log.addHandler(logging.StreamHandler(sys.stdout))
    oauth_log.setLevel(logging.DEBUG)

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'open_humans',

    # Studies
    'studies',
    'studies.american_gut',
    'studies.go_viral',
    'studies.pgp',

    # Activities
    'activities',
    'activities.twenty_three_and_me',

    # Other local apps
    'data_import',
    'public_data',

    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party modules
    'account',
    'corsheaders',
    'debug_toolbar.apps.DebugToolbarConfig',
    'django_extensions',
    'django_forms_bootstrap',
    'oauth2_provider',
    'rest_framework',
    'social.apps.django_app.default',
    'sorl.thumbnail',

    'raven.contrib.django.raven_compat',
)

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',

    'open_humans.middleware.RedirectStealthToProductionMiddleware',
    'open_humans.middleware.RedirectStagingToProductionMiddleware',

    'django.middleware.cache.UpdateCacheMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    # Must come before AuthenticationMiddleware
    'open_humans.middleware.QueryStringAccessTokenToBearerMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'account.middleware.LocaleMiddleware',
    'account.middleware.TimezoneMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',

    'account.context_processors.account',

    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
) + global_settings.TEMPLATE_CONTEXT_PROCESSORS

ROOT_URLCONF = 'open_humans.urls'

WSGI_APPLICATION = 'open_humans.wsgi.application'

# Default to sqlite; set DATABASE_URL to override
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Only override the default if there's a database URL specified
if dj_database_url.config():
    DATABASES['default'] = dj_database_url.config()

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'static-files')

STATICFILES_DIRS = (
    # Do this one manually since bootstrap wants it in ../fonts/
    ('fonts', os.path.join(BASE_DIR, 'static', 'vendor', 'bootstrap', 'dist',
                           'fonts')),
    ('images', os.path.join(BASE_DIR, 'static', 'images')),

    # Local apps
    ('public-data', os.path.join(BASE_DIR, 'public_data', 'static')),

    # Studies and activities must be stored according to the app's label
    ('twenty_three_and_me',
     os.path.join(BASE_DIR, 'activities', 'twenty_three_and_me', 'static')),
    ('american_gut',
     os.path.join(BASE_DIR, 'studies', 'american_gut', 'static')),
    ('go_viral', os.path.join(BASE_DIR, 'studies', 'go_viral', 'static')),
    ('pgp', os.path.join(BASE_DIR, 'studies', 'pgp', 'static')),

    os.path.join(BASE_DIR, 'build'),
)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'my-member-dashboard'

ACCOUNT_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_OPEN_SIGNUP = to_bool('ACCOUNT_OPEN_SIGNUP', 'true')
ACCOUNT_PASSWORD_MIN_LEN = 8
ACCOUNT_SIGNUP_REDIRECT_URL = 'my-member-signup-setup-1'
ACCOUNT_HOOKSET = 'open_humans.hooksets.OpenHumansHookSet'

DEFAULT_FROM_EMAIL = 'Open Humans <support@openhumans.org>'

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'no-reply@openhumans.org'
EMAIL_HOST_PASSWORD = os.getenv('MAILGUN_PASSWORD')
EMAIL_PORT = 587

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# TODO: Collect these programatically
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read Access',
        'write': 'Write Access',
        'american-gut': 'American Gut',
        'go-viral': 'GoViral',
        'pgp': 'Harvard Personal Genome Project',
        'open-humans': 'Open Humans',
    },
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 60 * 30,
    'REQUEST_APPROVAL_PROMPT': 'auto',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',

    'common.oauth_backends.TwentyThreeAndMeOAuth2',
)

DATA_PROCESSING_URL = os.getenv('DATA_PROCESSING_URL')

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

GO_VIRAL_MANAGEMENT_TOKEN = os.getenv('GO_VIRAL_MANAGEMENT_TOKEN')

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_S3_STORAGE_BUCKET_NAME')

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']

SOCIAL_AUTH_23ANDME_KEY = os.getenv('23ANDME_KEY')
SOCIAL_AUTH_23ANDME_SECRET = os.getenv('23ANDME_SECRET')
SOCIAL_AUTH_23ANDME_SCOPE = ['basic', 'names', 'genomes']

RAVEN_CONFIG = {
    'dsn': os.getenv('SENTRY_DSN'),
    'processors': (
        'common.processors.SanitizeEnvProcessor',
        'raven.processors.SanitizePasswordsProcessor',
    )
}

# Allow Cross-Origin requests (for our API integrations)
CORS_ORIGIN_ALLOW_ALL = True

# ...but only for the API URLs
CORS_URLS_REGEX = r'^/api/.*$'

SITE = FakeSite(DOMAIN)
SITE_ID = 1

# Import this last as it's going to import settings itself...
from django.contrib.sites import models as sites_models

# HACK: django-user-accounts uses both get_current_site and Site.get_current.
# The former falls back to a RequestSite if django.contrib.sites is not in
# INSTALLED_APPS. The latter tries to look up the site in the database but
# first hits the SITE_CACHE, which we prime here.
sites_models.SITE_CACHE[SITE_ID] = SITE

# This way of setting the memcache options is advised by MemCachier here:
# https://devcenter.heroku.com/articles/memcachier#django
if ENV == 'production' or ENV == 'staging':
    memcache_servers = os.getenv('MEMCACHIER_SERVERS', '').replace(',', ';')

    memcache_username = os.getenv('MEMCACHIER_USERNAME')
    memcache_password = os.getenv('MEMCACHIER_PASSWORD')

    if memcache_servers:
        os.environ['MEMCACHE_SERVERS'] = memcache_servers

    if memcache_username and memcache_password:
        os.environ['MEMCACHE_USERNAME'] = memcache_username
        os.environ['MEMCACHE_PASSWORD'] = memcache_password

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'BINARY': True,
        'OPTIONS': {
            'ketama': True,
            'tcp_nodelay': True,
        }
    }
}

if os.getenv('CI_NAME') == 'codeship':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

CACHE_MIDDLEWARE_SECONDS = 30 * 60

TEST_RUNNER = 'open_humans.OpenHumansDiscoverRunner'

# For redirecting staging URLs with production client IDs to production; this
# helps us transition new integrations from staging to production
PRODUCTION_CLIENT_IDS = os.getenv('PRODUCTION_CLIENT_IDS', '').split(' ')
PRODUCTION_URL = os.getenv('PRODUCTION_URL')

MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_NEWSLETTER_LIST = os.getenv('MAILCHIMP_NEWSLETTER_LIST')

# Import settings from local_settings.py; these override the above
try:
    # pylint: disable=wildcard-import
    from local_settings import *  # NOQA
    # pylint: enable=wildcard-import
except ImportError:
    pass
