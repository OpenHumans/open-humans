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

import dj_database_url

from .utilities import apply_env, get_env

# Apply the env in the .env file
apply_env(get_env())

from django.conf import global_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8_wdo-deqqh@7nbxf^uxasm4q*2+2n1qhr2*j+6khkri1jvb6)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG
OAUTH2_DEBUG = False

if DEBUG:
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

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Only override the default if there's a database URL specified
# NOTE: This will change as we add staging/production configurations
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

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'oh-data-export-testing-20141020'

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

# Import settings from local_settings.py; these override the above
try:
    from local_settings import *
except ImportError:
    pass
