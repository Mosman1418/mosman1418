from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from app.memorials.views import *

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mosman1418.views.home', name='home'),
    # url(r'^mosman1418/', include('mosman1418.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^memorials/$', show_memorials),
    url(r'^memorials/(?P<id>\d+)/$', show_memorial),
    url(r'^memorials/(?P<id>\d+)\.rdf/$', show_memorial_rdf),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('cms.urls')),
    url(r'^', include('filer.server.urls')),
)

if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
