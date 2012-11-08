from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from app.people.views import PersonView, PersonListView, StoryView, StoryListView, ImageView, ImageListView
from app.sources.views import SourceView
from app.memorials.views import MemorialView

admin.autodiscover()


    # Examples:
    # url(r'^$', 'mosman1418.views.home', name='home'),
    # url(r'^mosman1418/', include('mosman1418.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:

urlpatterns = patterns('app.sources.views',
    url(r'^sources/$', 'show_sources'),
    url(r'^sources/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', SourceView.as_view()),
    url(r'^sources/(?P<id>\d+)/$', SourceView.as_view(), name='source_view'),
)
urlpatterns += patterns('app.people.views',
    url(r'^people/$', PersonListView.as_view(), name="people_list"),
    url(r'^people/results\.(?P<format>(html|rdf|json|ttl))/$', PersonListView.as_view()),
    url(r'^people/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', PersonView.as_view()),
    url(r'^people/(?P<id>\d+)/$', PersonView.as_view(), name='person_view'),

    url(r'^stories/$', StoryListView.as_view(), name="story_list"),
    url(r'^stories/results\.(?P<format>(html|rdf|json|ttl))/$', StoryListView.as_view()),
    url(r'^stories/(?P<id>\d+)/$', StoryView.as_view(), name='view_story'),
    url(r'^stories/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', StoryView.as_view()),
    url(r'^stories/add/$', 'add_story'),
    url(r'^stories/add/(?P<entity_type>person)/(?P<id>\d+)$', 'add_story', name='person_add_story'),
    url(r'^stories/delete/(?P<id>\d+)/$', 'delete_story', name='delete_story'),
    url(r'^stories/edit/(?P<id>\d+)/$', 'edit_story', name='edit_story'),

    url(r'^images/$', ImageListView.as_view(), name="image_list"),
    url(r'^images/results\.(?P<format>(html|rdf|json|ttl))/$', ImageListView.as_view()),
    url(r'^images/(?P<id>\d+)/$', ImageView.as_view(), name='view_image'),
    url(r'^images/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', ImageView.as_view()),
    url(r'^images/add/$', 'add_image'),
    url(r'^images/add/(?P<entity_type>person)/(?P<id>\d+)$', 'add_image', name='person_add_image'),
    url(r'^images/delete/(?P<id>\d+)/$', 'delete_image', name='delete_image'),
    url(r'^images/edit/(?P<id>\d+)/$', 'edit_image', name='edit_image'),

    url(r'^people/autocomplete/$', 'person_autocomplete'),
)
urlpatterns += patterns('app.memorials.views',
    url(r'^memorials/$', 'show_memorials'),
    url(r'^memorials/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', MemorialView.as_view()),
    url(r'^memorials/(?P<id>\d+)/$', MemorialView.as_view(), name='memorial_view'),
)
urlpatterns += patterns('',
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
