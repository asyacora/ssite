# Django settings for djangoProject project.

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-r9^$(#zhu^1@(xt=1bbzzr=eyy!8!a$exqphy%0kohbx-8ovnf"

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
    "category",
    'accounts',
    'store',
    'carts',
    'orders',

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

ROOT_URLCONF = "djangoProject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'category.context_processors.menu_links',
                'carts.context_processors.counter',
            ],
        },
    },
]

WSGI_APPLICATION = "djangoProject.wsgi.application"

AUTH_USER_MODEL = 'accounts.Account'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / 'static'  # Specify a separate directory for STATIC_ROOT
STATICFILES_DIRS = [
    BASE_DIR / 'djangoProject/static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# SMTP Configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'client.asya@gmail.com'
EMAIL_HOST_PASSWORD = 'fkpb ovzw eqis yojs'
EMAIL_USE_TLS = True


STRIPE_SECRET_KEY_TEST = 'sk_test_51PKdxTEvA4zMMdKT97g0Vw6sv3ekDQ48wqcD8kX4e7pUBbT3ARD0bBa3EBgmGT5mZ51pM2P4hVItah2LaYkpgWUZ00sh2wNz5s'
STRIPE_PUBLISHABLE_KEY = 'pk_test_51PKdxTEvA4zMMdKTEqBkRjcAuUfrS5sMLyPZATYyVEeeJZCtJQwvOOqHDoMrZGiaipLeNkDBfh3XATxAD80KxpWi00TKllejsw'
PRODUCT_PRICE = 'price_1PKeGfEvA4zMMdKTh6rtb9e0'
REDIRECT_DOMAIN = 'http://127.0.0.1:8000'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field





DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
