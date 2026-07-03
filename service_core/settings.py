"""
Django settings for service_provider2 project.
"""

from pathlib import Path
import environ
from datetime import timedelta
# ------------------------------------------------------------------------------
# BASE DIRECTORY
# ------------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# ------------------------------------------------------------------------------

env = environ.Env(
    DEBUG=(bool, True)
)

environ.Env.read_env(BASE_DIR / ".env")

# ------------------------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------------------------

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = []

# ------------------------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third Party Apps
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",

    # Local Apps
    "apps.user",
    "apps.customer",
    "apps.provider",
    "apps.services",
    "apps.bookings",
]


# ------------------------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "service_core.urls"

# ------------------------------------------------------------------------------
# TEMPLATES
# ------------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "service_core.wsgi.application"


# ------------------------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# ------------------------------------------------------------------------------
# PASSWORD VALIDATORS
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ------------------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# ------------------------------------------------------------------------------
# STATIC & MEDIA FILES
# ------------------------------------------------------------------------------

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"
AUTH_USER_MODEL = "user.User"

# ------------------------------------------------------------------------------
# DJANGO REST FRAMEWORK
# ------------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ------------------------------------------------------------------------------
# SWAGGER SETTINGS
# ------------------------------------------------------------------------------

SPECTACULAR_SETTINGS = {
    "TITLE": "Service Provider API",
    "DESCRIPTION": "Service Provider Marketplace Backend APIs",
    "VERSION": "1.0.0",
    "ENUM_NAME_OVERRIDES": {
        "UserRoleEnum": "apps.user.models.User.Role",
    },
}

# ------------------------------------------------------------------------------
# DEFAULT PRIMARY KEY
# ------------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "AUTH_HEADER_TYPES": ("Bearer",),
}