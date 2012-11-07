from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from app.memorials.views import *
from app.people.views import *
from app.sources.views import *

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mosman1418.views.home', name='home'),
    # url(r'^mosman1418/', include('mosman1418.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^sources/$', show_sources),
    url(r'^sources/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', SourceView.as_view()),
    url(r'^sources/(?P<id>\d+)/$', SourceView.as_view(), name='source_view'),
    url(r'^people/$', show_people, name="people_list"),
    url(r'^people/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', PersonView.as_view()),
    url(r'^people/(?P<id>\d+)/$', PersonView.as_view(), name='person_view'),
    url(r'^people/story/(?P<id>\d+)/$', PeopleStoryView.as_view(), name='story_view'),
    url(r'^people/story/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', PeopleStoryView.as_view()),
    url(r'^people/story/add/$', add_story),
    url(r'^people/story/delete/(?P<id>\d+)/$', delete_story, name='people_delete_story'),
    url(r'^people/story/edit/(?P<id>\d+)/$', edit_story, name='people_edit_story'),
    url(r'^people/(?P<id>\d+)/story/add/$', add_story, name='people_add_story'),
    url(r'^people/autocomplete/$', person_autocomplete),
    url(r'^memorials/$', show_memorials),
    url(r'^memorials/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', MemorialView.as_view()),
    url(r'^memorials/(?P<id>\d+)/$', MemorialView.as_view(), name='memorial_view'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    #url(r'^', include('cms.urls')),
    #url(r'^', include('filer.server.urls')),
)

if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
