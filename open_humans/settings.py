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

from env_tools import apply_env


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
apply_env()

# Detect when the tests are being run so we can diable certain features
TESTING = 'test' in sys.argv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PORT = os.getenv('PORT', 8000)

ENV = os.getenv('ENV', 'development')
DOMAIN = os.getenv('DOMAIN', 'localhost:{}'.format(PORT))

DEFAULT_HTTP_PROTOCOL = 'http'

if ENV in ['production', 'staging']:
    # For email template URLs
    DEFAULT_HTTP_PROTOCOL = 'https'

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = to_bool('DEBUG')
OAUTH2_DEBUG = to_bool('OAUTH2_DEBUG')

# This is the default but we need it here to make migrations work
OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'

# Disable SSL during development
SSLIFY_DISABLE = ENV not in ['production', 'staging']

LOG_EVERYTHING = to_bool('LOG_EVERYTHING')

DISABLE_CACHING = to_bool('DISABLE_CACHING')

ALLOW_TOKEN_REFRESH = to_bool('ALLOW_TOKEN_REFRESH')

# The number of hours after which a direct upload is assumed to be incomplete
# if the uploader hasn't hit the completion endpoint
INCOMPLETE_FILE_EXPIRATION_HOURS = 6

if os.getenv('CI_NAME') == 'codeship':
    DISABLE_CACHING = True

console_at_info = {
    'handlers': ['console'],
    'level': 'INFO',
}

null = {
    'handlers': ['null'],
}

IGNORE_SPURIOUS_WARNINGS = to_bool('IGNORE_SPURIOUS_WARNINGS')

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
elif not TESTING:
    LOGGING = {
        'disable_existing_loggers': False,
        'version': 1,
        'formatters': {
            'open-humans': {
                '()': 'open_humans.formatters.LocalFormat',
                'format': '%(levelname)s %(asctime)s %(context)s %(message)s',
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
            'common': console_at_info,
            'data_import': console_at_info,
            'open_humans': console_at_info,
            'public_data': console_at_info,
        },
    }
else:
    LOGGING = {
        'disable_existing_loggers': True,
        'version': 1,
        'formatters': {},
        'handlers': {
            'null': {
                'class': 'logging.NullHandler'
            },
        },
        'loggers': {
            'django.request': null,
            'common': null,
            'data_import': null,
            'open_humans': null,
            'public_data': null,
        }
    }

if IGNORE_SPURIOUS_WARNINGS:
    LOGGING['handlers']['null'] = {
        'class': 'logging.NullHandler'
    }

    LOGGING['loggers']['py.warnings'] = {
        'handlers': ['null']
    }

if OAUTH2_DEBUG:
    oauth_log = logging.getLogger('oauthlib')

    oauth_log.addHandler(logging.StreamHandler(sys.stdout))
    oauth_log.setLevel(logging.DEBUG)

ALLOWED_HOSTS = ['*']

MANAGERS = ()
ADMINS = ()

INSTALLED_APPS = (
    'open_humans',

    # Studies
    #'studies',
    #'studies.american_gut',
    #'studies.go_viral',
    #'studies.pgp',
    #'studies.wildlife',

    # Activities
    #'activities',
    #'activities.data_selfie',
    #'activities.fitbit',
    #'activities.jawbone',
    #'activities.moves',
    #'activities.mpower',
    #'activities.runkeeper',
    #'activities.withings',
    #'activities.twenty_three_and_me',
    #'activities.ancestry_dna',
    #'activities.ubiome',
    #'activities.vcf_data',

    # Other local apps
    'data_import',
    'private_sharing',
    'public_data',

    # gulp integration
    'django_gulp',

    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party modules
    'account',
    'bootstrap_pagination',
    'captcha',
    'corsheaders',
    # 'debug_toolbar.apps.DebugToolbarConfig',
    'django_extensions',
    'django_forms_bootstrap',
    'django_hash_filter',
    'oauth2_provider',
    'rest_framework',
    's3upload',
    'social.apps.django_app.default',
    'sorl.thumbnail',
)

if not TESTING:
    INSTALLED_APPS = INSTALLED_APPS + ('raven.contrib.django.raven_compat',)

    RAVEN_CONFIG = {
        'dsn': os.getenv('SENTRY_DSN'),
        'processors': (
            'common.processors.SanitizeEnvProcessor',
            'raven.processors.SanitizePasswordsProcessor',
        )
    }

MIDDLEWARE_CLASSES = (
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
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

    'open_humans.middleware.AddMemberMiddleware',
    'open_humans.middleware.PGPInterstitialRedirectMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',
)

template_context_processors = [
    'account.context_processors.account',

    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',

    'django.template.context_processors.request',

    'django.contrib.auth.context_processors.auth',

    'django.template.context_processors.debug',
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',

    'django.contrib.messages.context_processors.messages',
]

template_loaders = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

# Don't cache templates during development
if not DEBUG and not DISABLE_CACHING:
    template_loaders = [
        ('django.template.loaders.cached.Loader', template_loaders)
    ]

template_options = {
    'context_processors': template_context_processors,
    'debug': DEBUG,
    'loaders': template_loaders,
}

NOBROWSER = to_bool('NOBROWSER', 'false')

if TESTING:
    from .testing import InvalidString  # pylint: disable=wrong-import-position

    template_options['string_if_invalid'] = InvalidString('%s')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': template_options,
    },
    # {
    #     'BACKEND': 'django.template.backends.jinja2.Jinja2',
    #     'OPTIONS': {
    #         'loader': template_loaders
    #     },
    # },
]

ROOT_URLCONF = 'open_humans.urls'

WSGI_APPLICATION = 'open_humans.wsgi.application'

# Use DATABASE_URL to do database setup, for a local Postgres database it would
# look like: postgres://localhost/database_name
DATABASES = {}

# Only override the default if there's a database URL specified
if os.getenv('CI_NAME') == 'codeship':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test',
        'USER': os.getenv('PG_USER'),
        'PASSWORD': os.getenv('PG_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': 5434
    }
elif dj_database_url.config():
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
    ('fonts', os.path.join(BASE_DIR, 'node_modules', 'bootstrap', 'dist',
                           'fonts')),
    ('images', os.path.join(BASE_DIR, 'static', 'images')),

    # Local apps
    ('public-data', os.path.join(BASE_DIR, 'public_data', 'static')),
    ('direct-sharing', os.path.join(BASE_DIR, 'private_sharing', 'static')),

    os.path.join(BASE_DIR, 'build'),
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'home'

AUTH_USER_MODEL = 'open_humans.User'

ACCOUNT_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_OPEN_SIGNUP = to_bool('ACCOUNT_OPEN_SIGNUP', 'true')
ACCOUNT_PASSWORD_MIN_LEN = 8
ACCOUNT_SIGNUP_REDIRECT_URL = 'home'
ACCOUNT_HOOKSET = 'open_humans.hooksets.OpenHumansHookSet'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'home'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'home'
ACCOUNT_USE_AUTH_AUTHENTICATE = True

# We want CREATE_ON_SAVE to be True (the default) unless we're using the
# `loaddata` command--because there's a documented issue in loading fixtures
# that include accounts:
# http://django-user-accounts.readthedocs.org/en/latest/usage.html#including-accounts-in-fixtures
ACCOUNT_CREATE_ON_SAVE = sys.argv[1:2] != ['loaddata']

DEFAULT_FROM_EMAIL = 'Open Humans <support@openhumans.org>'

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'no-reply@openhumans.org'
EMAIL_HOST_PASSWORD = os.getenv('MAILGUN_PASSWORD')
EMAIL_PORT = 587

# Fall back to console emails for development without mailgun set.
if DEBUG and not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social.backends.jawbone.JawboneOAuth2',
    'social.backends.moves.MovesOAuth2',
    'social.backends.runkeeper.RunKeeperOAuth2',
    'common.oauth_backends.WithingsOAuth1',
    'common.oauth_backends.FitbitOAuth2',
)

GO_VIRAL_MANAGEMENT_TOKEN = os.getenv('GO_VIRAL_MANAGEMENT_TOKEN')

DATA_PROCESSING_URL = os.getenv('DATA_PROCESSING_URL')

DEFAULT_FILE_STORAGE = 'open_humans.storage.PrivateStorage'

# COLORSPACE and PRESERVE_FORMAT to avoid transparent PNG turning black, see
# https://stackoverflow.com/questions/26762180/sorl-thumbnail-generates-black-square-instead-of-image
THUMBNAIL_STORAGE = 'open_humans.storage.PublicStorage'
THUMBNAIL_FORCE_OVERWRITE = True
THUMBNAIL_COLORSPACE = None
THUMBNAIL_PRESERVE_FORMAT = True

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_S3_STORAGE_BUCKET_NAME')

# "On projects behind a reverse proxy that uses HTTPS, the redirect URIs can
# became with the wrong schema (http:// instead of https://) when the request
# lacks some headers, and might cause errors with the auth process, to force
# HTTPS in the final URIs set this setting to True"
if ENV in ['production', 'staging']:
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',

    # Not needed unless we're auto-creating users
    # 'social.pipeline.user.get_username',

    # NOTE: this might be useful for UYG
    # Associates the current social details with another user account with
    # a similar email address.
    # 'social.pipeline.social_auth.associate_by_email',

    # If `create_user` is included in the pipeline then social will create new
    # accounts if the user isn't logged into Open Humans--meaning that if a
    # user logs in with RunKeeper they get an auto-generated Open Humans
    # account, which isn't the behavior we want.
    # 'social.pipeline.user.create_user',

    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

SOCIAL_AUTH_FITBIT_KEY = os.getenv('FITBIT_ID')
SOCIAL_AUTH_FITBIT_SECRET = os.getenv('FITBIT_SECRET')

SOCIAL_AUTH_FITBIT_SCOPE = [
    # The activity scope includes activity data and exercise log related
    # features, such as steps, distance, calories burned, and active minutes
    'activity',
    # The heartrate scope includes the continuous heart rate data and related
    # analysis
    'heartrate',
    # The location scope includes the GPS and other location data
    'location',
    # The nutrition scope includes calorie consumption and nutrition related
    # features, such as food/water logging, goals, and plans
    'nutrition',
    # The profile scope is the basic user information
    # 'profile',
    # The settings scope includes user account and device settings, such as
    # alarms
    # 'settings',
    # The sleep scope includes sleep logs and related sleep analysis
    'sleep',
    # The social scope includes friend-related features, such as friend list,
    # invitations, and leaderboard
    # 'social',
    # The weight scope includes weight and related information, such as body
    # mass index, body fat percentage, and goals
    'weight',
]

SOCIAL_AUTH_JAWBONE_KEY = os.getenv('JAWBONE_ID')
SOCIAL_AUTH_JAWBONE_SECRET = os.getenv('JAWBONE_SECRET')

SOCIAL_AUTH_JAWBONE_SCOPE = [
    'basic_read',
    'extended_read',
    'generic_event_read',
    'heartrate_read',
    'location_read',
    'meal_read',
    'mood_read',
    'move_read',
    'sleep_read',
    'weight_read',
]

SOCIAL_AUTH_MOVES_SCOPE = [
    'activity',
    'location',
]

SOCIAL_AUTH_MOVES_KEY = os.getenv('MOVES_ID')
SOCIAL_AUTH_MOVES_SECRET = os.getenv('MOVES_SECRET')

SOCIAL_AUTH_RUNKEEPER_KEY = os.getenv('RUNKEEPER_ID')
SOCIAL_AUTH_RUNKEEPER_SECRET = os.getenv('RUNKEEPER_SECRET')

SOCIAL_AUTH_WITHINGS_KEY = os.getenv('WITHINGS_ID')
SOCIAL_AUTH_WITHINGS_SECRET = os.getenv('WITHINGS_SECRET')

# Allow Cross-Origin requests (for our API integrations)
CORS_ORIGIN_ALLOW_ALL = True

# Custom CSRF Failure page
CSRF_FAILURE_VIEW = 'open_humans.views.csrf_error'

# ...but only for the API URLs
CORS_URLS_REGEX = r'^/api/.*$'

SITE = FakeSite(DOMAIN)
SITE_ID = 1

# This way of setting the memcache options is advised by MemCachier here:
# https://devcenter.heroku.com/articles/memcachier#django
if ENV in ['production', 'staging']:
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

if DISABLE_CACHING:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

CACHE_MIDDLEWARE_SECONDS = 30 * 60

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

TEST_RUNNER = 'open_humans.OpenHumansDiscoverRunner'

# For redirecting staging URLs with production client IDs to production; this
# helps us transition new integrations from staging to production
PRODUCTION_CLIENT_IDS = os.getenv('PRODUCTION_CLIENT_IDS', '').split(' ')
PRODUCTION_URL = os.getenv('PRODUCTION_URL')

MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_NEWSLETTER_LIST = os.getenv('MAILCHIMP_NEWSLETTER_LIST')

NOCAPTCHA = True

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

ZAPIER_WEBHOOK_URL = os.getenv('ZAPIER_WEBHOOK_URL')

MAX_UNAPPROVED_MEMBERS = int(os.getenv('MAX_UNAPPROVED_MEMBERS', '20'))

# Highlighted projects
PROJ_FEATURED = os.getenv('PROJ_FEATURED', None)

# The key used to communicate between this site and data-processing
PRE_SHARED_KEY = os.getenv('PRE_SHARED_KEY')

# Import settings from local_settings.py; these override the above
try:
    # pylint: disable=wildcard-import,wrong-import-position
    from local_settings import *  # NOQA
except ImportError:
    pass
