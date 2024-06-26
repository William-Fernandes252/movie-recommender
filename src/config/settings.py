"""
Django settings for movie-recommender project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

from celery.schedules import crontab
from decouple import config
from dj_database_url import parse as db_url
from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Admins
ADMINS = ["William Fernandes <william.winchester1967@gmail.com>"]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG")


# Hosting policy

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default=["*"], cast=lambda v: [s.strip() for s in v.split(",")]
)


# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS: list[str] = [
    "django_celery_beat",
    "django_celery_results",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_htmx",
]

LOCAL_APPS: list[str] = [
    "users",
    "movies",
    "ratings",
    "exports",
    "suggestions",
    "dashboard",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]


ROOT_URLCONF = "config.urls"


SITE_ID = 1


# Templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ratings.context_processors.rating_choices",
            ],
        },
    },
]


# Messages

MESSAGE_TAGS = {message_constants.ERROR: "danger"}


# WSGI configuration.

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": config(
        "DATABASE_URL", default=f'sqlite:///{BASE_DIR / "db.sqlite3"}', cast=db_url
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
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


# Authentication

AUTH_USER_MODEL = "users.User"

LOGIN_URL = "/accounts/login/"

LOGIN_REDIRECT_URL = "/"

ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_VERIFICATION = None


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Celery

CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BEAT_SCHEDULE = {
    "update_outdated_movie_ratings_every_10_min": {
        "task": "update_movie_ratings_outdated",
        "schedule": 60 * 10,
    },
    "update_movie_indexes_daily": {
        "task": "update_movie_position_embeddings",
        "schedule": crontab(hour=1, minute=0),
    },
    "export_movie_ratings_dataset_daily": {
        "task": "export_movie_ratings_dataset",
        "schedule": crontab(hour=1, minute=15),
    },
    "export_movies_dataset_daily": {
        "task": "export_movies_dataset",
        "schedule": crontab(hour=2, minute=30),
    },
    "train_and_export_movie_recommendation_model_daily": {
        "task": "train_and_export_surprise_model",
        "schedule": crontab(hour=3, minute=0),
    },
    "batch_create_movie_suggestions_daily": {
        "task": "batch_user_prediction",
        "schedule": crontab(hour=4, minute=30),
        "kwargs": {"max": 5000, "offset": 200},
    },
}

# Media

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "media"
