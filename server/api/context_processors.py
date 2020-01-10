from django.conf import settings

def exposed_settings(request):
  return {'settings': settings}
