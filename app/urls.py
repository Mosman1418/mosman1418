from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from app.people.views import *
from app.sources.views import *
from app.places.views import *
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
    url(r'^sources/(?P<id>\d+)/$', SourceView.as_view(), name='source-view'),
    url(r'^sources/add/$', AddSourceView.as_view(), name='source-add'),
    url(r'^sources/add/(?P<entity_type>person)/(?P<entity_id>\d+)$', AddSourceView.as_view(), name='source-add-person'),
    url(r'^sources/add/(?P<event_type>(births|deaths|lifeevents|names))/(?P<event_id>\d+)/$', AddSourceView.as_view(), name='source-add-event'),
    url(r'^sources/(?P<pk>\d+)/update/$', UpdateSourceView.as_view(), name='source-update'),
    url(r'^sources/add/(?P<source_type>(collection|part))/(?P<source_id>\d+)$', AddSourceView.as_view(), name='source-add-source'),
    url(r'^sources/(?P<source_id>\d+)/creator/add/$', AddSourcePersonView.as_view(), name='source-creator-add'),
)
urlpatterns += patterns('app.people.views',
    url(r'^people/$', PersonListView.as_view(), name="people-list"),
    url(r'^people/results\.(?P<format>(html|rdf|json|ttl))/$', PersonListView.as_view()),
    url(r'^people/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', PersonView.as_view()),
    url(r'^people/(?P<id>\d+)/$', PersonView.as_view(), name='person-view'),

    url(r'^people/add/$', AddPerson.as_view(), name="person-add"),
    url(r'^people/(?P<pk>\d+)/update/$', UpdatePerson.as_view(), name="person-update"),

    url(r'^people/names/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', AltNameView.as_view()),
    url(r'^people/names/(?P<id>\d+)/$', AltNameView.as_view(), name='altname-view'),
    url(r'^people/names/(?P<pk>\d+)/update/$', UpdateAltName.as_view(), name='altname-update'),
    url(r'^people/(?P<person_id>\d+)/names/add/$', AddAltName.as_view(), name='altname-add'),
    url(r'^people/names/(?P<pk>\d+)/delete/$', DeleteAltName.as_view(), name='altname-delete'),

    url(r'^people/births/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', BirthView.as_view()),
    url(r'^people/births/(?P<id>\d+)/$', BirthView.as_view(), name='birth-view'),
    url(r'^people/births/(?P<pk>\d+)/update/$', UpdateBirth.as_view(), name='birth-update'),
    url(r'^people/(?P<person_id>\d+)/births/add/$', AddBirth.as_view(), name='birth-add'),
    url(r'^people/births/(?P<pk>\d+)/delete/$', DeleteBirth.as_view(), name='birth-delete'),

    url(r'^people/deaths/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', DeathView.as_view()),
    url(r'^people/deaths/(?P<id>\d+)/$', DeathView.as_view(), name='death-view'),
    url(r'^people/deaths/(?P<pk>\d+)/update/$', UpdateDeath.as_view(), name='death-update'),
    url(r'^people/(?P<person_id>\d+)/deaths/add/$', AddDeath.as_view(), name='death-add'),
    url(r'^people/deaths/(?P<pk>\d+)/delete/$', DeleteDeath.as_view(), name='death-delete'),

    url(r'^people/events/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', LifeEventView.as_view()),
    url(r'^people/events/(?P<id>\d+)/$', LifeEventView.as_view(), name='lifeevent-view'),
    url(r'^people/events/(?P<pk>\d+)/update/$', UpdateLifeEvent.as_view(), name='lifeevent-update'),
    url(r'^people/(?P<person_id>\d+)/events/add/$', AddLifeEvent.as_view(), name='lifeevent-add'),
    url(r'^people/events/(?P<pk>\d+)/delete/$', DeleteLifeEvent.as_view(), name='lifeevent-delete'),

    url(r'^people/events/locations/(?P<pk>\d+)/update/$', UpdateEventLocation.as_view(), name='eventlocation-update'),
    url(r'^people/events/(?P<event_id>\d+)/locations/add/$', AddEventLocation.as_view(), name='eventlocation-add'),
    url(r'^people/events/locations/(?P<pk>\d+)/delete/$', DeleteEventLocation.as_view(), name='eventlocation-delete'),

    url(r'^stories/$', StoryListView.as_view(), name="story_list"),
    url(r'^stories/results\.(?P<format>(html|rdf|json|ttl))/$', StoryListView.as_view()),
    url(r'^stories/(?P<id>\d+)/$', StoryView.as_view(), name='view_story'),
    url(r'^stories/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', StoryView.as_view()),
    url(r'^stories/add/$', 'add_story', name='add_story'),
    url(r'^stories/add/(?P<entity_type>person)/(?P<id>\d+)$', 'add_story', name='person_add_story'),
    url(r'^stories/delete/(?P<id>\d+)/$', 'delete_story', name='delete_story'),
    url(r'^stories/edit/(?P<id>\d+)/$', 'edit_story', name='edit_story'),

    url(r'^images/$', ImageListView.as_view(), name="image_list"),
    url(r'^images/results\.(?P<format>(html|rdf|json|ttl))/$', ImageListView.as_view()),
    url(r'^images/(?P<id>\d+)/$', ImageView.as_view(), name='view_image'),
    url(r'^images/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', ImageView.as_view()),
    url(r'^images/add/$', 'add_image', name='add_image'),
    url(r'^images/add/(?P<entity_type>person)/(?P<id>\d+)$', 'add_image', name='person_add_image'),
    url(r'^images/delete/(?P<id>\d+)/$', 'delete_image', name='delete_image'),
    url(r'^images/edit/(?P<id>\d+)/$', 'edit_image', name='edit_image'),

    url(r'^places/$', PlaceListView.as_view(), name="place-list"),
    url(r'^places/results\.(?P<format>(html|rdf|json|ttl))/$', PlaceListView.as_view()),
    url(r'^places/(?P<id>\d+)/$', PlaceView.as_view(), name='place-view'),
    url(r'^places/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', PlaceView.as_view()),
    url(r'^places/(?P<pk>\d+)/update/$', UpdatePlace.as_view(), name='place-update'),
    url(r'^places/add/(?P<event_type>(births|deaths|lifeevents))/(?P<event_id>\d+)/$', AddPlace.as_view(), name='place-add-event'),
    url(r'^places/add/$', AddPlace.as_view(), name='place-add'),
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

urlpatterns += patterns("",
    url(r"^select2/", include("django_select2.urls")),
)

if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
