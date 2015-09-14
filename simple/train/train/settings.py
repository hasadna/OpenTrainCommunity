"""
Django settings for train project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kco-o6ho_i@mgfjo!9gajorxg&rg=3m3kap^^#$mzbe%j1^@ne'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',
    'train',
    'data',
    'browse',
    'csvparser',
    'xlparser'

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'data.middleware.OpenTrainMiddleware',
)

ROOT_URLCONF = 'train.urls'

WSGI_APPLICATION = 'train.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = None

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'HE'

TIME_ZONE = 'Asia/Jerusalem'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (os.path.join(BASE_DIR,'locale'),)

# Static files (CSS, JavaScript, Images)django.db.backends
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/home/opentrain/public_html/static/'

CORS_ORIGIN_ALLOW_ALL = True

OT_LOG_DIR = '/var/log/opentrain'

LOGGING = {
    'version' : 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple' : {
            'format' : "==========================================\n[%(asctime)s %(levelname)s] %(message)s"
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(OT_LOG_DIR,'error.log'),
            'formatter' : 'simple',
        },
    },
    'loggers': {
        'errors': {
            'handlers': ['file'],
        },
    },
}

TXT_FOLDER = os.path.join(BASE_DIR, 'csvparser/unzip_data')

try:
    from .local_settings import *
except ImportError:
    pass

try:
    from local_settings import *
except ImportError:
    pass
