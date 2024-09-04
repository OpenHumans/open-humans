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
import django_heroku

from env_tools import apply_env
import re

def to_bool(env, default="false"):
    """
    Convert a string to a bool.
    """
    return bool(util.strtobool(os.getenv(env, default)))


# Apply the env in the .env file
apply_env()

# Detect when the tests are being run so we can disable certain features
TESTING = "test" in sys.argv

# ON_HEROKU should be true if we are running on heroku.
ON_HEROKU = to_bool("ON_HEROKU")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PORT = os.getenv("PORT", 8000)

ENV = os.getenv("ENV", "development")
# ENV = 'staging'
DOMAIN = os.getenv("DOMAIN", "localhost:{}".format(PORT))

DEFAULT_HTTP_PROTOCOL = "http"

if ENV in ["production", "staging"]:
    # For email template URLs
    DEFAULT_HTTP_PROTOCOL = "https"

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = to_bool("DEBUG")
OAUTH2_DEBUG = to_bool("OAUTH2_DEBUG")

# This is the default but we need it here to make migrations work
OAUTH2_PROVIDER_APPLICATION_MODEL = "oauth2_provider.Application"

LOG_EVERYTHING = to_bool("LOG_EVERYTHING")

DISABLE_CACHING = to_bool("DISABLE_CACHING")

ALLOW_TOKEN_REFRESH = to_bool("ALLOW_TOKEN_REFRESH")

# The number of hours after which a direct upload is assumed to be incomplete
# if the uploader hasn't hit the completion endpoint
INCOMPLETE_FILE_EXPIRATION_HOURS = 6

if os.getenv("CI_NAME") == "codeship":
    DISABLE_CACHING = True

console_at_info = {"handlers": ["console"], "level": "INFO"}

null = {"handlers": ["null"]}

IGNORE_SPURIOUS_WARNINGS = to_bool("IGNORE_SPURIOUS_WARNINGS")

if LOG_EVERYTHING:
    LOGGING = {
        "disable_existing_loggers": False,
        "version": 1,
        "handlers": {"console": {"class": "logging.StreamHandler", "level": "DEBUG"}},
        "loggers": {
            "": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
            "django.db": {
                # django also has database level logging
            },
        },
    }
elif not TESTING:
    LOGGING = {
        "disable_existing_loggers": False,
        "version": 1,
        "formatters": {
            "open-humans": {
                "()": "open_humans.formatters.LocalFormat",
                "format": "%(levelname)s %(asctime)s %(context)s %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "open-humans",
            }
        },
        "loggers": {
            "django.request": console_at_info,
            # Log our modules at INFO
            "common": console_at_info,
            "data_import": console_at_info,
            "open_humans": console_at_info,
            "public_data": console_at_info,
        },
    }
else:
    LOGGING = {
        "disable_existing_loggers": True,
        "version": 1,
        "formatters": {},
        "handlers": {"null": {"class": "logging.NullHandler"}},
        "loggers": {
            "django.request": null,
            "common": null,
            "data_import": null,
            "open_humans": null,
            "public_data": null,
        },
    }

if IGNORE_SPURIOUS_WARNINGS:
    LOGGING["handlers"]["null"] = {"class": "logging.NullHandler"}

    LOGGING["loggers"]["py.warnings"] = {"handlers": ["null"]}

if OAUTH2_DEBUG:
    oauth_log = logging.getLogger("oauthlib")

    oauth_log.addHandler(logging.StreamHandler(sys.stdout))
    oauth_log.setLevel(logging.DEBUG)

ALLOWED_HOSTS = ["*"]

CELERY_BROKER_URL = os.getenv("REDIS_URL")
CELERY_TASK_SERIALIZER = "json"

MANAGERS = ()
ADMINS = ()

INSTALLED_APPS = (
    "open_humans",
    # Other local apps
    "data_import",
    "private_sharing",
    "public_data",
    "discourse",
    # gulp integration
    "django_gulp",
    # Django built-ins
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party modules
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.apple",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.google",
    "bootstrap_pagination",
    "django_recaptcha",
    "corsheaders",
    # 'debug_toolbar.apps.DebugToolbarConfig',
    "django_extensions",
    "django_filters",
    "django_forms_bootstrap",
    "django_hash_filter",
    "oauth2_provider",
    "rest_framework",
    "s3upload",
    "sorl.thumbnail",
    "waffle",
)

MIDDLEWARE = (
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "open_humans.middleware.RedirectStealthToProductionMiddleware",
    "open_humans.middleware.RedirectStagingToProductionMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # Must come before AuthenticationMiddleware
    "open_humans.middleware.QueryStringAccessTokenToBearerMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "open_humans.middleware.AddMemberMiddleware",
    "open_humans.middleware.CustomWaffleMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
)

template_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

# Don't cache templates during development
if not DEBUG and not DISABLE_CACHING:
    template_loaders = [("django.template.loaders.cached.Loader", template_loaders)]

NOBROWSER = to_bool("NOBROWSER", "false")

if TESTING:
    from .testing import InvalidString  # pylint: disable=wrong-import-position

    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": DEBUG,
        },
    }
]

if os.getenv("BULK_EMAIL_TEMPLATE_DIR"):
    TEMPLATES[0]["DIRS"].append(os.getenv("BULK_EMAIL_TEMPLATE_DIR"))

ROOT_URLCONF = "open_humans.urls"

WSGI_APPLICATION = "open_humans.wsgi.application"

# Use DATABASE_URL to do database setup, for a local Postgres database it would
# look like: postgres://localhost/database_name
DATABASES = {}

# Only override the default if there's a database URL specified
if os.getenv("CI_NAME") == "codeship":
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "test",
        "USER": os.getenv("PG_USER"),
        "PASSWORD": os.getenv("PG_PASSWORD"),
        "HOST": "127.0.0.1",
        "PORT": 5434,
    }
elif not ON_HEROKU and dj_database_url.config():
    DATABASES["default"] = dj_database_url.config()

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, "static-files")

STATICFILES_DIRS = (
    # Do this one manually since bootstrap wants it in ../fonts/
    ("fonts", os.path.join(BASE_DIR, "node_modules", "bootstrap", "dist", "fonts")),
    ("images", os.path.join(BASE_DIR, "static", "images")),
    # Local apps
    ("public-data", os.path.join(BASE_DIR, "public_data", "static")),
    ("direct-sharing", os.path.join(BASE_DIR, "private_sharing", "static")),
    os.path.join(BASE_DIR, "build"),
)

STATIC_URL = "/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "home"

AUTH_USER_MODEL = "open_humans.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    }
]

ACCOUNT_ADAPTER = "common.adapters.MyAccountAdapter"
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
# currently ignored due to custom User and ModelBackend (see above)
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_PASSWORD_MIN_LENGTH = 8
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USERNAME_VALIDATORS = "open_humans.models.ohusernamevalidators"
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_USERNAME_BLACKLIST = ["admin", "administrator", "moderator", "openhuman"]

SOCIALACCOUNT_ADAPTER = "common.adapters.MySocialAccountAdapter"
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_EMAIL_VERIFICATION = False
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {"SCOPE": ["profile", "email"], "AUTH_PARAMS": {"access_type": "online"}},
    "facebook": {
        "METHOD": "oauth2",
        "SCOPE": ["email", "public_profile"],
        "AUTH_PARAMS": {"auth_type": "https"},
        "INIT_PARAMS": {"cookie": True},
        "FIELDS": [
            "email",
            "name",
            "first_name",
            "last_name",
            "verified",
            "locale",
            "timezone",
        ],
        "EXCHANGE_TOKEN": True,
        "LOCALE_FUNC": "path.to.callable",
        "VERIFIED_EMAIL": False,
        "VERSION": "v2.12",
    },
}


DEFAULT_FROM_EMAIL = "Open Humans <support@openhumans.org>"

EMAIL_USE_TLS = True

EMAIL_HOST = "smtp.mailgun.org"
EMAIL_HOST_USER = "no-reply@openhumans.org"
EMAIL_HOST_PASSWORD = os.getenv("MAILGUN_PASSWORD")
EMAIL_PORT = 587

# Fall back to console emails for development without mailgun set.
if DEBUG and not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# TODO: Collect these programatically
OAUTH2_PROVIDER = {
    "PKCE_REQUIRED": False,
    "SCOPES": {
        "read": "Read Access",
        "write": "Write Access",
        "american-gut": "American Gut",
        "go-viral": "GoViral",
        "pgp": "Harvard Personal Genome Project",
        "wildlife": "Wildlife of Our Homes",
        "open-humans": "Open Humans",
    },
    "AUTHORIZATION_CODE_EXPIRE_SECONDS": 60 * 30,
    "REQUEST_APPROVAL_PROMPT": "auto",
    "ALLOWED_REDIRECT_URI_SCHEMES": [
        "http",
        "https",
        # Redirect URIs that are using iOS or Android app-registered schema
        "openhumanshk",
        "resilienceproject",
    ]
    + [
        x
        for x in os.getenv("OAUTH2_PROVIDER_ALLOWED_REDIRECT_URI_SCHEMES", "").split(
            ","
        )
        if x
    ],
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Settings for django-waffle.
WAFFLE_FLAG_MODEL = "open_humans.FeatureFlag"

# ModelBackend before allauth + our User -> iexact email/username login
AUTHENTICATION_BACKENDS = (
    "oauth2_provider.backends.OAuth2Backend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

GO_VIRAL_MANAGEMENT_TOKEN = os.getenv("GO_VIRAL_MANAGEMENT_TOKEN")

DATA_PROCESSING_URL = os.getenv("DATA_PROCESSING_URL")

DEFAULT_FILE_STORAGE = "open_humans.storage.PrivateStorage"

# COLORSPACE and PRESERVE_FORMAT to avoid transparent PNG turning black, see
# https://stackoverflow.com/questions/26762180/sorl-thumbnail-generates-black-square-instead-of-image
THUMBNAIL_STORAGE = "open_humans.storage.PublicStorage"
THUMBNAIL_FORCE_OVERWRITE = True
THUMBNAIL_COLORSPACE = None
THUMBNAIL_PRESERVE_FORMAT = True

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_S3_STORAGE_BUCKET_NAME")
AWS_DEFAULT_ACL = None  # This will become default in django-storages 2.0
LOG_BUCKET = os.getenv("LOG_BUCKET")

# Allow Cross-Origin requests (for our API integrations)
CORS_ORIGIN_ALLOW_ALL = True

# Custom CSRF Failure page
CSRF_FAILURE_VIEW = "open_humans.views.csrf_error"

# ...but only for the API URLs
CORS_URLS_REGEX = r"^/api/.*$"

SITE_ID = 1


# This way of setting the memcache options is advised by MemCachier here:
# https://devcenter.heroku.com/articles/memcachier#django
if ENV in ["production", "staging"]:
    memcache_servers = os.getenv("MEMCACHIER_SERVERS", None)
    memcache_username = os.getenv("MEMCACHIER_USERNAME", None)
    memcache_password = os.getenv("MEMCACHIER_PASSWORD", None)

    if memcache_servers and memcache_username and memcache_password:
        CACHES = {
            "default": {
                # Use django-bmemcached
                "BACKEND": "django_bmemcached.memcached.BMemcached",

                # TIMEOUT is default expiration for keys; None disables expiration.
                "TIMEOUT": None,

                "LOCATION": memcache_servers,

                "OPTIONS": {
                    "username": memcache_username,
                    "password": memcache_password,
                }
            }
        }

if DISABLE_CACHING:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

CACHE_MIDDLEWARE_SECONDS = 30 * 60

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

TEST_RUNNER = "open_humans.OpenHumansDiscoverRunner"

# For redirecting staging URLs with production client IDs to production; this
# helps us transition new integrations from staging to production
PRODUCTION_CLIENT_IDS = os.getenv("PRODUCTION_CLIENT_IDS", "").split(" ")
PRODUCTION_URL = os.getenv("PRODUCTION_URL")

MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_NEWSLETTER_LIST = os.getenv("MAILCHIMP_NEWSLETTER_LIST")

NOCAPTCHA = True

RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY", "")
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY", "")
RECAPTCHA_REQUIRED_SCORE = os.getenv("RECAPTCHA_REQUIRED_SCORE", "0.5")

OHLOG_PROJECT_ID = os.getenv("OHLOG_PROJECT_ID", None)

ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")

DISCOURSE_BASE_URL = os.getenv("DISCOURSE_BASE_URL", "https://forums.openhumans.org")

DISCOURSE_SSO_SECRET = os.getenv("DISCOURSE_SSO_SECRET")

MAX_UNAPPROVED_MEMBERS = int(os.getenv("MAX_UNAPPROVED_MEMBERS", "20"))

# Highlighted projects
PROJ_FEATURED = os.getenv("PROJ_FEATURED", None)

# The key used to communicate between this site and data-processing
PRE_SHARED_KEY = os.getenv("PRE_SHARED_KEY")

# Import settings from local_settings.py; these override the above
try:
    # pylint: disable=wildcard-import,wrong-import-position
    from local_settings import *  # NOQA
except ImportError:
    pass

DISALLOWED_USER_AGENTS = [
    re.compile(r'.*DotBot.*'),
    re.compile(r'.*AhrefsBot.*'),
    re.compile(r'SemrushBot.*'),
    re.compile(r'.*Barkrowler.*'),
    re.compile(r'.*meta-external.*'),
    re.compile(r'.*facebook-external.*'),
    re.compile(r'.*GPTBot.*'),
    re.compile(r'.*AmazonBot.*'),
    re.compile(r'.*GoogleBot.*'),
    re.compile(r'.*AmazonBot.*'),
    re.compile(r'.*bingbot.*'),
    re.compile(r'.*PetalBot.*')
]

if ON_HEROKU:
    INSTALLED_APPS = INSTALLED_APPS + ("raven.contrib.django.raven_compat",)

    RAVEN_CONFIG = {
        "dsn": os.getenv("SENTRY_DSN"),
        "processors": (
            "common.processors.SanitizeEnvProcessor",
            "raven.processors.SanitizePasswordsProcessor",
        ),
    }

    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    django_heroku.settings(locals())
