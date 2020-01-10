from server import settings

from django.contrib import admin

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from jsonrpc import jsonrpc_site, views

import api.views

admin.autodiscover()

urlpatterns = [
  url(r'^-/api/$', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),
  url(r'^-/api/browse/', views.browse, name='jsonrpc_browser'),

  #url(r'^grappelli/', include('grappelli.urls')),
  url(r'^-/admin/', include(admin.site.urls)),

  # Uncomment the admin/doc line below to enable admin documentation:
  # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
] + \
static('/client', document_root='../client/dist') + \
static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
