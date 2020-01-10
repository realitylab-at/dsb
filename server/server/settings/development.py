# -*- coding: utf-8 -*-

from os import path
from common import *

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = True

#DEBUG_TOOLBAR_PATCH_SETTINGS = False

APP_PATH = path.dirname(path.abspath(__file__)) + '/../..'

MEDIA_ROOT = '%s/upload/' % APP_PATH
STATIC_ROOT = '%s/static/' % APP_PATH

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': '%s/infoboard.db' % APP_PATH
  }
}

ALLOWED_HOSTS += ('infoboard',)

INSTALLED_APPS += (
  #'debug_toolbar',
  'django_extensions',
)

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/infoboard/mail'

if DEBUG == True:
  import warnings
  warnings.filterwarnings('error', r"DateTimeField received a naive datetime", RuntimeWarning, r'django\.db\.models\.fields')
