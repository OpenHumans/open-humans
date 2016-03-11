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

from django.conf import global_settings  # noqa pylint: disable=wrong-import-position

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
            'activities': null,
            'common': null,
            'data_import': null,
            'open_humans': null,
            'public_data': null,
            'studies': null,
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
    'studies',
    'studies.american_gut',
    'studies.go_viral',
    'studies.pgp',
    'studies.wildlife',

    # Activities
    'activities',
    'activities.data_selfie',
    'activities.fitbit',
    'activities.moves',
    'activities.runkeeper',
    'activities.withings',
    'activities.twenty_three_and_me',
    'activities.ancestry_dna',
    'activities.illumina_uyg',
    'activities.ubiome',

    # Other local apps
    'data_import',
    'private_sharing',
    'public_data',
    'discourse',

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
    'django_hosts',
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
    'django_hosts.middleware.HostsRequestMiddleware',
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
    'django_hosts.middleware.HostsResponseMiddleware',
)

template_context_processors = [
    'django.template.context_processors.request',

    'account.context_processors.account',

    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
] + global_settings.TEMPLATE_CONTEXT_PROCESSORS

# Don't cache templates during development
if DEBUG or DISABLE_CACHING:
    template_loaders = global_settings.TEMPLATE_LOADERS
else:
    template_loaders = [
        (
            'django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        )
    ]


template_options = {
    'context_processors': template_context_processors,
    'debug': DEBUG,
    'loaders': template_loaders,
}

if TESTING:
    from .testing import InvalidString

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

# For django_hosts setup
ROOT_HOSTCONF = 'open_humans.hosts'
DEFAULT_HOST = 'main'

# The top-level domain that django-hosts subdomains are parented under
PARENT_HOST = os.getenv('PARENT_HOST', 'openhumans.org')

# The domain that the research site is accessible from
RESEARCH_HOST = os.getenv('RESEARCH_HOST', 'research')

STATIC_ROOT = os.path.join(BASE_DIR, 'static-files')

STATICFILES_DIRS = (
    # Do this one manually since bootstrap wants it in ../fonts/
    ('fonts', os.path.join(BASE_DIR, 'node_modules', 'bootstrap', 'dist',
                           'fonts')),
    ('images', os.path.join(BASE_DIR, 'static', 'images')),

    # Local apps
    ('public-data', os.path.join(BASE_DIR, 'public_data', 'static')),

    # Third-party studies
    ('studies', os.path.join(BASE_DIR, 'studies', 'static')),

    # Studies and activities must be stored according to the app's label
    ('fitbit', os.path.join(BASE_DIR, 'activities', 'fitbit', 'static')),
    ('illumina_uyg', os.path.join(BASE_DIR, 'activities', 'illumina_uyg', 'static')),
    ('moves', os.path.join(BASE_DIR, 'activities', 'moves', 'static')),
    ('runkeeper', os.path.join(BASE_DIR, 'activities', 'runkeeper', 'static')),
    ('ubiome', os.path.join(BASE_DIR, 'activities', 'ubiome', 'static')),
    ('withings', os.path.join(BASE_DIR, 'activities', 'withings', 'static')),
    ('twenty_three_and_me',
     os.path.join(BASE_DIR, 'activities', 'twenty_three_and_me', 'static')),
    ('ancestry_dna',
     os.path.join(BASE_DIR, 'activities', 'ancestry_dna', 'static')),
    ('american_gut',
     os.path.join(BASE_DIR, 'studies', 'american_gut', 'static')),
    ('go_viral', os.path.join(BASE_DIR, 'studies', 'go_viral', 'static')),
    ('pgp', os.path.join(BASE_DIR, 'studies', 'pgp', 'static')),
    ('wildlife', os.path.join(BASE_DIR, 'studies', 'wildlife', 'static')),

    os.path.join(BASE_DIR, 'build'),
)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'welcome'

AUTH_USER_MODEL = 'open_humans.User'

ACCOUNT_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_OPEN_SIGNUP = to_bool('ACCOUNT_OPEN_SIGNUP', 'true')
ACCOUNT_PASSWORD_MIN_LEN = 8
ACCOUNT_SIGNUP_REDIRECT_URL = 'welcome'
ACCOUNT_HOOKSET = 'open_humans.hooksets.OpenHumansHookSet'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'welcome'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'welcome'
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
    'social.backends.moves.MovesOAuth2',
    'social.backends.runkeeper.RunKeeperOAuth2',
    'social.backends.withings.WithingsOAuth',
    'common.oauth_backends.FitbitOAuth2',
)

GO_VIRAL_MANAGEMENT_TOKEN = os.getenv('GO_VIRAL_MANAGEMENT_TOKEN')

DATA_PROCESSING_URL = os.getenv('DATA_PROCESSING_URL')

DEFAULT_FILE_STORAGE = 'open_humans.storage.PrivateStorage'

THUMBNAIL_STORAGE = 'open_humans.storage.PublicStorage'
THUMBNAIL_FORCE_OVERWRITE = True

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_S3_STORAGE_BUCKET_NAME')

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

# TODO: This could be part of the activity, if we start to add more of these
# and want them to be more self-contained.
PROVIDER_NAME_MAPPING = {
    'fitbit': 'Fitbit',
    'moves': 'Moves',
    'runkeeper': 'RunKeeper',
    'withings': 'Withings',
}

# Allow Cross-Origin requests (for our API integrations)
CORS_ORIGIN_ALLOW_ALL = True

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

DISCOURSE_BASE_URL = os.getenv('DISCOURSE_BASE_URL',
                               'https://forums.openhumans.org')

DISCOURSE_SSO_SECRET = os.getenv('DISCOURSE_SSO_SECRET')

# Import settings from local_settings.py; these override the above
try:
    # pylint: disable=wildcard-import
    from local_settings import *  # NOQA
    # pylint: enable=wildcard-import
except ImportError:
    pass
