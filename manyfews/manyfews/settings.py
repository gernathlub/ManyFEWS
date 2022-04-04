"""
Django settings for manyfews project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# =======================================================================================
# These settings can be updated by setting environment variables or adding to a .env file
# =======================================================================================

# Database details
DB_NAME = env.str("db_name", "manyfews")
DB_USER = env.str("db_user", "manyfews")
DB_PASSWORD = env.str("db_password", "manyfews")
DB_HOST = env.str("db_host", "localhost")
DB_PORT = env.int("db_port", 5432)

# Zentra account and station details
ZENTRA_UN = env.str("zentra_un")
ZENTRA_PW = env.str("zentra_pw")
ZENTRA_BACKTIME = env.float("zentra_backtime", 1)
STATION_SN = env.str("station_SN", "06-02047")

# GEFS weather forecast details
GEFS_TIME_STEP = env.float("gefs_timestep", 0.25)
GEFS_FORECAST_DAYS = env.int("gefs_forecastDays", 16)
LAT_VALUE = env.float("latValue", -80.5)
LON_VALUE = env.float("lonValue", 175)

# Thresholds for number of m^2 cells that count towards flood risk
# CHANNEL_CELL_COUNT is number of cells in the river channel
CHANNEL_CELL_COUNT = env.int("channel_cell_count", 93794)
# LARGE_FLOOD_COUNT is number of cells that represent a large area of flooding
LARGE_FLOOD_COUNT = env.int("large_flood_count", 1440811)

# Leaflet map tiles URL (including API key if needed)
MAP_URL = env.str(
    "map_url", "https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}{r}.png"
)
MAP_CENTER = env.tuple("map_center", float, (-7.050465729629079, 107.75813455787436))

# Email settings
EMAIL_HOST = env.str("email_host", "smtp.gmail.com")
EMAIL_PORT = env.int("email_port", 465)
EMAIL_HOST_USER = env.str("email_host_user", "")
EMAIL_HOST_PASSWORD = env.str("email_host_password", "")
EMAIL_USE_SSL = env.bool("email_use_ssl", True)

# Twilio settings (for SMS/WhatsApp)
TWILIO_ACCOUNT_SID = env.str("twilio_account_sid", "")
TWILIO_AUTH_TOKEN = env.str("twilio_auth_token", "")
TWILIO_PHONE_NUMBER = env.str("twilio_phone_number", "")
TWILIO_VERIFICATION_SID = env.str("twilio_verification_sid", "")

# Site URL (or short URL) for use in messages
SITE_URL = env.str("site_url", "http://localhost:8000")

# Text to use in alerts. Will be populated with max_depth, start and end dates and SITE_URL
ALERT_TEXT = env.str(
    "alert_text",
    "Floods up to {max_depth}m predicted from {start_date} to {end_date}. See {site_url} for details.",
)
# Date string to use in alerts: for formats see https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
ALERT_DATE_FORMAT = env.str("alert_date_format", "%b %d")
ALERT_DEPTH_THRESHOLD = env.float("alert_depth_threshold", 0.1)

# =======================================================================================
# End of user configurable settings
# =======================================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-jau(^3c!z+wl6#zsz!%bu1$v7ks48dosj1#=l=^+58)r1y2n8b"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_celery_beat",
    "crispy_forms",
    "djgeojson",
    "leaflet",
    "phonenumber_field",
    "calculations",
    "webapp",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "manyfews.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR.joinpath("templates"))],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "webapp.context_processors.include_login_form",
            ],
        },
    },
]

WSGI_APPLICATION = "manyfews.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRISPY_TEMPLATE_PACK = "bootstrap4"

LEAFLET_CONFIG = {
    "DEFAULT_CENTER": MAP_CENTER,
    "DEFAULT_ZOOM": 18,
    "MIN_ZOOM": 10,
    "MAX_ZOOM": 25,
    "DEFAULT_PRECISION": 6,
    "TILES": MAP_URL,
}

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
