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

# pylint: disable=no-name-in-module
from distutils import util
# pylint: enable=no-name-in-module

import dj_database_url

from .utilities import apply_env, get_env


def to_bool(env, default='false'):
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
    'easy_thumbnails',
    'oauth2_provider',
    'rest_framework',
    'social.apps.django_app.default',

    'raven.contrib.django.raven_compat',
)

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'account.middleware.LocaleMiddleware',
    'account.middleware.TimezoneMiddleware',
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
    os.path.join(BASE_DIR, 'build'),
)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CRISPY_TEMPLATE_PACK = 'bootstrap3'

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'my-member-dashboard'
ACCOUNT_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_SIGNUP_REDIRECT_URL = 'my-member-signup-setup-1'

DEFAULT_FROM_EMAIL = 'Open Humans <support@openhumans.org>'

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'no-reply@openhumans.org'
EMAIL_HOST_PASSWORD = os.getenv('MAILGUN_PASSWORD')
EMAIL_PORT = 587

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# TODO: Collect these programatically?
OAUTH2_PROVIDER = {
    'SCOPES': {
        # XXX: Do read and write make sense on their own?
        'read': 'The ability to read your data',
        'write': 'The ability to write your data',
        'american-gut': 'Access to your American Gut Data',
        'go-viral': 'Access to your GoViral data',
        'pgp': 'Access to your Personal Genome Project data',
    },
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

# Import settings from local_settings.py; these override the above
try:
    # pylint: disable=wildcard-import
    from local_settings import *  # NOQA
    # pylint: enable=wildcard-import
except ImportError:
    pass
