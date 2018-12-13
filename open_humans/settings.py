"""
Django settings for open_humans project.

"""

import os
import sys

from distutils import util  # pylint: disable=no-name-in-module

from env_tools import apply_env


# Apply the env in the .env file
apply_env()


def to_bool(env, default='false'):
    """
    Convert a string to a bool.
    """
    return bool(util.strtobool(os.getenv(env, default)))


################################################################################
# Below this line are the basic settings provided by Django.  Do not add       #
# additional configuration options here.                                       #
################################################################################

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = to_bool('DEBUG')

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    # Our apps
    'open_humans',
    'data_import',
    'private_sharing',
    'public_data',

    # django builtins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party modules
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'bootstrap_pagination',
    'captcha',
    'corsheaders',
    'django_extensions',
    'django_filters',
    'django_forms_bootstrap',
    'django_gulp',
    'django_hash_filter',
    'oauth2_provider',
    'rest_framework',
    's3upload',
    'sorl.thumbnail',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'open_humans.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'



################################################################################
# Above this line are the basic settings provided by django (as modified to    #
# work for us).  Below this line are additional settings for open-humans.      #
# Please keep these settings in alphabetical order unless required otherwise.  #
################################################################################

# Settings that other settings depend on

PORT = os.getenv('PORT', '8000')
DOMAIN = os.getenv('DOMAIN', 'localhost:{}'.format(PORT))

CI = os.getenv('CI_NAME') == 'codeship'

# Note:  from here on, the standard way of detecting if we are running in heroku
# or not is by setting the env var ON_HEROKU.  This is true of staging, prod,
# and any test instance that may be setup.
ON_HEROKU = to_bool(os.getenv('ON_HEROKU', 'false'))
if ON_HEROKU:
    DEFAULT_HTTP_PROTOCOL = 'https'
else:
    DEFAULT_HTTP_PROTOCOL = 'http'

# Detect when the tests are being run so we can disable certain features
TESTING = 'test' in sys.argv


# Settings are alphabetical from here


# ModelBackend before allauth + our User -> iexact email/username login
AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

DATABASES = {}

DEFAULT_FROM_EMAIL = 'Open Humans <support@openhumans.org>'

DISABLE_CACHING = to_bool('DISABLE_CACHING')

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'no-reply@openhumans.org'
EMAIL_HOST_PASSWORD = os.getenv('MAILGUN_PASSWORD')
EMAIL_PORT = 587

# Fall back to console emails for development without mailgun set.
if not ON_HEROKU or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# The number of hours after which a direct upload is assumed to be incomplete
# if the uploader hasn't hit the completion endpoint
INCOMPLETE_FILE_EXPIRATION_HOURS = 6

LOG_EVERYTHING = to_bool('LOG_EVERYTHING')

# TODO: Collect these programatically
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read Access',
        'write': 'Write Access',
        'american-gut': 'American Gut',
        'go-viral': 'GoViral',
        'pgp': 'Harvard Personal Genome Project',
        'wildlife': 'Wildlife of Our Homes',
        'open-humans': 'Open Humans',
    },
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 60 * 30,
    'REQUEST_APPROVAL_PROMPT': 'auto',
    'ALLOWED_REDIRECT_URI_SCHEMES': [
        'http', 'https',
        # Redirect URIs that are using iOS or Android app-registered schema
        'openhumanshk', 'resilienceproject',
    ],
}

OAUTH2_DEBUG = to_bool('OAUTH2_DEBUG')

# This is the default but we need it here to make migrations work
OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SITE_ID = 1

# Disable SSL during development
SSLIFY_DISABLE = not ON_HEROKU


# Activate Django-Heroku.
# Note that we only want to do this if we're actually on heroku, as
# django-heroku hard-codes using ssl.
if ON_HEROKU:
    import django_heroku
    django_heroku.settings(locals())
else:
    # for local running; djang-heroku hard codes ssl_require, this let's us
    # run locally without having to setup ssl certs and the like.
    if CI:
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'test',
            'USER': os.getenv('PG_USER'),
            'PASSWORD': os.getenv('PG_PASSWORD'),
            'HOST': '127.0.0.1',
            'PORT': 5434
        }
    else:
        import dj_database_url
        DATABASES['default'] = dj_database_url.config(ssl_require=False)

# Import settings from local_settings.py; these override the above
try:
    # pylint: disable=wildcard-import,wrong-import-position
    from local_settings import *  # NOQA
except ImportError:
    pass
