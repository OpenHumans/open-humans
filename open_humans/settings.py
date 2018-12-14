"""
Django settings for open_humans project.

"""

import os
import sys

from distutils import util  # pylint: disable=no-name-in-module

from env_tools import apply_env


# Apply the env in the .env file
apply_env()


# Various helpers go here

def to_bool(env, default='false'):
    """
    Convert a string to a bool.
    """
    return bool(util.strtobool(os.getenv(env, default)))

console_at_info = {
    'handlers': ['console'],
    'level': 'INFO',
}

null = {
    'handlers': ['null'],
}


# Note:  from here on, the standard way of detecting if we are running in heroku
# or not is by setting the env var ON_HEROKU.  This is true of staging, prod,
# and any test instance that may be setup.
ON_HEROKU = to_bool(os.getenv('ON_HEROKU', 'false'))


################################################################################
# Below this line are the basic settings provided by Django.  Do not add       #
# additional configuration options here.                                       #
################################################################################

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not ON_HEROKU:
    SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = to_bool('DEBUG')

if not ON_HEROKU:
    ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    # Our apps
    'open_humans',
    'data_import',
    'private_sharing',
    'public_data',

    # gulp integration
    'django_gulp',

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
    'django_hash_filter',
    'oauth2_provider',
    'rest_framework',
    's3upload',
    'sorl.thumbnail',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'open_humans.middleware.AddMemberMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'open_humans.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
            },
    },
]

if os.getenv('BULK_EMAIL_TEMPLATE_DIR'):
    TEMPLATES[0]['DIRS'].append(os.getenv('BULK_EMAIL_TEMPLATE_DIR'))

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

OAUTH2_DEBUG = to_bool('OAUTH2_DEBUG')

if ON_HEROKU:
    DEFAULT_HTTP_PROTOCOL = 'https'
else:
    DEFAULT_HTTP_PROTOCOL = 'http'

if not ON_HEROKU:
    ENV = 'development'
else:
    os.getenv('ENV', 'development')

# Detect when the tests are being run so we can disable certain features
TESTING = 'test' in sys.argv


# Settings are alphabetical from here

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
# currently ignored due to custom User and ModelBackend
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_PASSWORD_MIN_LENGTH = 8
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_VALIDATORS = 'open_humans.models.ohusernamevalidators'
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_USERNAME_BLACKLIST = ['admin',
                              'administrator',
                              'moderator',
                              'openhuman']

# We want CREATE_ON_SAVE to be True (the default) unless we're using the
# `loaddata` command--because there's a documented issue in loading fixtures
# that include accounts:
# http://django-user-accounts.readthedocs.org/en/latest/usage.html#including-accounts-in-fixtures
ACCOUNT_CREATE_ON_SAVE = sys.argv[1:2] != ['loaddata']

AUTH_USER_MODEL = 'open_humans.User'

# ModelBackend before allauth + our User -> iexact email/username login
AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_S3_STORAGE_BUCKET_NAME')
AWS_DEFAULT_ACL = None  # This will become default in django-storages 2.0

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

if CI:
    DISABLE_CACHING = True
else:
    DISABLE_CACHING = to_bool('DISABLE_CACHING')

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

# Allow Cross-Origin requests (for our API integrations)
CORS_ORIGIN_ALLOW_ALL = True

# Custom CSRF Failure page
CSRF_FAILURE_VIEW = 'open_humans.views.csrf_error'

# ...but only for the API URLs
CORS_URLS_REGEX = r'^/api/.*$'

DATABASES = {}

DEFAULT_FILE_STORAGE = 'open_humans.storage.PrivateStorage'

DEFAULT_FROM_EMAIL = 'Open Humans <support@openhumans.org>'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'no-reply@openhumans.org'
EMAIL_HOST_PASSWORD = os.getenv('MAILGUN_PASSWORD')
EMAIL_PORT = 587

# Fall back to console emails for development without mailgun set.
if not ON_HEROKU or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

IGNORE_SPURIOUS_WARNINGS = to_bool('IGNORE_SPURIOUS_WARNINGS')

# The number of hours after which a direct upload is assumed to be incomplete
# if the uploader hasn't hit the completion endpoint
INCOMPLETE_FILE_EXPIRATION_HOURS = 6

if ON_HEROKU:
    INSTALLED_APPS = INSTALLED_APPS + ('raven.contrib.django.raven_compat',)

    RAVEN_CONFIG = {
        'dsn': os.getenv('SENTRY_DSN'),
        'processors': (
            'common.processors.SanitizeEnvProcessor',
            'raven.processors.SanitizePasswordsProcessor',
        )
    }

LOG_EVERYTHING = to_bool(os.getenv('LOG_EVERYTHING'))

if not ON_HEROKU:
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

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'home'

MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_NEWSLETTER_LIST = os.getenv('MAILCHIMP_NEWSLETTER_LIST')

MAX_UNAPPROVED_MEMBERS = int(os.getenv('MAX_UNAPPROVED_MEMBERS', '20'))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

NOBROWSER = True

NOCAPTCHA = True

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

# This is the default but we need it here to make migrations work
OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'

# For redirecting staging URLs with production client IDs to production; this
# helps us transition new integrations from staging to production
PRODUCTION_CLIENT_IDS = os.getenv('PRODUCTION_CLIENT_IDS', '').split(' ')
PRODUCTION_URL = os.getenv('PRODUCTION_URL')

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

SITE_ID = 1

# Disable SSL during development
SSLIFY_DISABLE = not ON_HEROKU

if not ON_HEROKU:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
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

TEST_RUNNER = 'open_humans.OpenHumansDiscoverRunner'

# COLORSPACE and PRESERVE_FORMAT to avoid transparent PNG turning black, see
# https://stackoverflow.com/questions/26762180/sorl-thumbnail-generates-black-square-instead-of-image
THUMBNAIL_STORAGE = 'open_humans.storage.PublicStorage'
THUMBNAIL_FORCE_OVERWRITE = True
THUMBNAIL_COLORSPACE = None
THUMBNAIL_PRESERVE_FORMAT = True

WSGI_APPLICATION = 'open_humans.wsgi.application'


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
