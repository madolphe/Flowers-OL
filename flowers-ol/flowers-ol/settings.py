"""
Django settings for interface_experimentation project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Attempt to load SECRET_KEY from environment variable
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# If SECRET_KEY is missing, prompt the user to enter one (development use only)
if not SECRET_KEY:
    if os.getenv('DJANGO_ENV') == 'development':  # Only prompt in development
        SECRET_KEY = input("Enter your Django SECRET_KEY: ")
    else:
        raise ValueError("Missing DJANGO_SECRET_KEY in environment for production!")

SECURE_REFERRER_POLICY = 'same-origin'
# SECURE_HSTS_SECONDS = 3600*24*30
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['localhost', "127.0.0.1", "0.0.0.0"]
LOGIN_URL = '/signup_page/'

# Application definition
INSTALLED_APPS = [
    # Django contrib apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Django third party apps
    'background_task',
    'django_extensions',
    'crispy_forms',
    'modeltranslation'
]
USER_APPS = [
    # This is the list of user-defined apps
    'manager_app']
INSTALLED_APPS += USER_APPS  # append USER_APPS to list of INSTALLED_APPS
CRISPY_TEMPLATE_PACK = 'bootstrap4'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
ROOT_URLCONF = 'flowers-ol.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
WSGI_APPLICATION = 'flowers-ol.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'flowers-ol-db')
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LOCALE_PATHS = [
    os.path.join(os.path.dirname(__file__), "manager_app/locale"),
    os.path.join(os.path.dirname(__file__), "demo_app/locale")
]
LANGUAGE_CODE = 'fr'
LANGUAGES = [('fr', _('français')), ('en', _('english'))]
MODELTRANSLATION_AUTO_POPULATE = True
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
DATE_INPUT_FORMATS = ['%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d']
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Emails
EMAIL_HOST = 'smtp.inria.fr'
DEFAULT_FROM_EMAIL = 'noreply-flowers@inria.fr'
EMAIL_PORT = 25
EMAIL_USE_TLS = True
# For testing (on gmail)
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'yourUsername@gmail.com'
# EMAIL_HOST_PASSWORD = 'your_gmail_password'
# DEFAULT_FROM_EMAIL = 'yourUsername@gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

# SUPERUSER
DJANGO_SUPERUSER_USERNAME = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
DJANGO_SUPERUSER_PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin")
DJANGO_SUPERUSER_EMAIL = os.getenv("DJANGO_SUPERUSER_EMAIL", None)

# Background tasks
BACKGROUND_TASK_RUN_ASYNC = True  # if True, will run the tasks asynchronous. This means the tasks will be processed in parallel (at the same time) instead of processing one by one (one after the other).
MAX_ATTEMPTS = 10  # controls how many times a task will be attempted (default 25)
# MAX_RUN_TIME # maximum possible task run time, after which tasks will be unlocked and tried again (default 3600 seconds)
# BACKGROUND_TASK_ASYNC_THREADS # Specifies number of concurrent threads. Default is multiprocessing.cpu_count().
# BACKGROUND_TASK_PRIORITY_ORDERING # Control the ordering of tasks in the queue. Default is "DESC" (tasks with a higher number are processed first). Choose "ASC" to switch to the “niceness” ordering. A niceness of −20 is the highest priority and 19 is the lowest priority.
X_FRAME_OPTIONS = 'ALLOWALL'
