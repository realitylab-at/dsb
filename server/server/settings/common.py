# -*- coding: utf-8 -*-

from os import path
from local import *

ALLOWED_HOSTS = ('127.0.0.1',)
SECRET_KEY = SECRET_KEY

ADMINS = (
  ('Tobi Schäfer', 'mail@tobischaefer.com'),
)

MANAGERS = ADMINS

APP_PATH = path.dirname(path.abspath(__file__)) + '/../..'

TIME_ZONE = 'Europe/Vienna'
LANGUAGE_CODE = 'de-AT.UTF-8'

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = '/srv/www/dsb0/upload'
MEDIA_URL = '/upload/'

STATIC_ROOT = '/srv/www/dsb0/static'
STATIC_URL = '/static/'
STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
  #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'DIRS': [
      '%s/templates' % APP_PATH,
    ],
    'OPTIONS': {
      'context_processors': [
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.request',
        'django.core.context_processors.i18n',
        'django.contrib.messages.context_processors.messages',
        'django.core.context_processors.static',
        'api.context_processors.exposed_settings',
      ]
    }
  },
]

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'server.urls'

WSGI_APPLICATION = 'server.wsgi.application'

INSTALLED_APPS = (
  #'grappelli',

  # 'django.contrib.admindocs',
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.messages',
  'django.contrib.sessions',
  'django.contrib.staticfiles',

  'jsonrpc',
  'adminsortable',
  'reversion',
  'import_export',

  'api'
)

from django.core.exceptions import SuspiciousOperation

def skip_suspicious_operations(record):
  if record.exc_info:
    exc_value = record.exc_info[1]
    if isinstance(exc_value, SuspiciousOperation):
      return False
  return True

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'filters': {
    'require_debug_false': {
      '()': 'django.utils.log.RequireDebugFalse'
    },
    'skip_suspicious_operations': {
      '()': 'django.utils.log.CallbackFilter',
      'callback': skip_suspicious_operations,
    },
  },
  'handlers': {
    'mail_admins': {
      'level': 'ERROR',
      'filters': ['require_debug_false', 'skip_suspicious_operations'],
      'class': 'django.utils.log.AdminEmailHandler'
    }
  },
  'loggers': {
    'django.request': {
      'handlers': ['mail_admins'],
      'level': 'ERROR',
      'propagate': True,
    }
  }
}

TEMP_PASSWORD_EXPIRY = 1 # hour

SITE_TITLE = 'Digitales schwarzes Brett'
SITE_VERSION = '16.2.0'
