# -*- coding: utf-8 -*-

try:
  from local import SECRET_KEY
except:
  import sys
  sys.exit('SECRET_KEY is missing in server.settings.local module. Please add it and retry.')

from local import *
