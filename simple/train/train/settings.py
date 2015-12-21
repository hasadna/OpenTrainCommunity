"""
Django settings for train project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import tempfile

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
    'xlparser',
    'rest_framework'
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


DATABASES =  {
     'default': {
         'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'NAME': 'traindata',
         'USER': 'traindata',
         'PASSWORD': 'somepassword',
         'HOST': 'localhost',
         'PORT' : '5432'
     }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'HE'

TIME_ZONE = 'Asia/Jerusalem'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)

# Static files (CSS, JavaScript, Images)django.db.backends
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/home/opentrain/public_html/static/'

CORS_ORIGIN_ALLOW_ALL = True

TMP_ROOT = tempfile.gettempdir()


def find_ot_log_dir():
    ot_log_dir = '/var/log/opentrain'
    ot_log_dir2 = os.path.join(TMP_ROOT, 'opentrain_logs')
    try:
        if not os.path.exists(ot_log_dir):
            os.makedirs(ot_log_dir)
        return ot_log_dir
    except (OSError, IOError) as e:
        # print('>>> Failed to create {0}: {1} - falling back to {2}'.format(ot_log_dir,
        #                                                                    e,
        #                                                                    ot_log_dir2))
        if not os.path.exists(ot_log_dir2):
            os.makedirs(ot_log_dir2)
    return ot_log_dir2


OT_LOG_DIR = find_ot_log_dir()

TXT_FOLDER = '/home/opentrain/public_html/files/txt/'
EXCEL_FOLDER = '/home/opentrain/public_html/files/xl/'

CACHE_TTL = 30 * 24 * 60 * 60  # one month

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(TMP_ROOT, 'opentrain_cache')
    }
}

try:
    from .local_settings import *
except ImportError:
    pass

try:
    from local_settings import *
except ImportError:
    pass

USE_SQLITE3 = 'sqlite3' in DATABASES['default']['ENGINE']

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': "==========================================\n[%(asctime)s %(levelname)s] %(message)s"
        },
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(module)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%m/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(OT_LOG_DIR, 'error.log'),
            'formatter': 'simple',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'errors': {
            'handlers': ['file'],
        },
    },
}
