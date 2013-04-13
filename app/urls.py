from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from app.people.views import *
from app.sources.views import *
from app.places.views import *
from app.memorials.views import *
from app.base.views import *

admin.autodiscover()


    # Examples:
    # url(r'^$', 'mosman1418.views.home', name='home'),
    # url(r'^mosman1418/', include('mosman1418.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:

urlpatterns = patterns('app.sources.views',
    url(r'^sources/$', SourceListView.as_view(), name="source-list"),
    url(r'^sources/results\.(?P<format>(html|rdf|json|ttl))/$', SourceListView.as_view()),
    url(r'^sources/(?P<letter>[a-zA-Z]{1})/$', SourceListView.as_view(), name="source-alpha-list"),
    url(r'^sources/(?P<letter>[a-zA-Z]{1})/results\.(?P<format>(html|rdf|json|ttl))/$', SourceListView.as_view()),
    url(r'^sources/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', SourceView.as_view()),
    url(r'^sources/(?P<id>\d+)/$', SourceView.as_view(), name='source-view'),
    url(r'^sources/add/$', AddSourceView.as_view(), name='source-add'),
    #url(r'^sources/add/(?P<entity_type>person)/(?P<entity_id>\d+)/$', AddSourceView.as_view(), name='source-add-person'),
    url(r'^sources/add/(?P<entity_type>(person|mainperson|organisation|birth|death|lifeevent|name|rank|servicenumber|story|relationship|membership|address))/(?P<entity_id>\d+)/$', AddSourceView.as_view(), name='source-add-entity'),
    url(r'^sources/add/associations/(?P<assoc_type>(people|organisations|address|personorganisation))/(?P<assoc_id>\d+)/$', AddSourceView.as_view(), name='source-add-association'),
    url(r'^sources/(?P<pk>\d+)/update/$', UpdateSourceView.as_view(), name='source-update'),
    url(r'^sources/add/(?P<source_type>(collection|part))/(?P<source_id>\d+)/$', AddSourceView.as_view(), name='source-add-source'),
    url(r'^sources/(?P<pk>\d+)/delete/$', DeleteSource.as_view(), name='source-delete'),

    url(r'^images/$', ImageListView.as_view(), name="image-list"),
    url(r'^images/results\.(?P<format>(html|rdf|json|ttl))/$', ImageListView.as_view()),

    url(r'^stories/$', StoryListView.as_view(), name="story-list"),
    url(r'^stories/results\.(?P<format>(html|rdf|json|ttl))/$', StoryListView.as_view()),
    url(r'^stories/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', StoryView.as_view()),
    url(r'^stories/(?P<id>\d+)/$', StoryView.as_view(), name='story-view'),
    url(r'^stories/add/$', AddStory.as_view(), name='story-add'),
    url(r'^stories/add/(?P<entity_type>person)/(?P<entity_id>\d+)/$', AddStory.as_view(), name='story-add-entity'),
    url(r'^stories/(?P<pk>\d+)/update/$', UpdateStory.as_view(), name='story-update'),
    url(r'^stories/(?P<pk>\d+)/delete/$', DeleteStory.as_view(), name='story-delete'),
)
urlpatterns += patterns('app.people.views',
    url(r'^sources/(?P<source_id>\d+)/(?P<creator_type>(author|editor))/add/$', AddPerson.as_view(), name='source-creator-add'),
    url(r'^people/$', PersonListView.as_view(), name="people-list"),
    url(r'^people/(?P<letter>[a-zA-Z]{1})/$', PersonListView.as_view(), name="people-alpha-list"),
    url(r'^people/results\.(?P<format>(html|rdf|json|ttl))/$', PersonListView.as_view()),
    url(r'^people/(?P<letter>[a-zA-Z]{1})/results\.(?P<format>(html|rdf|json|ttl))/$', PersonListView.as_view()),
    url(r'^people/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', PersonView.as_view()),
    url(r'^people/(?P<id>\d+)/$', PersonView.as_view(), name='person-view'),
    url(r'^people/(?P<id>\d+)/photos\.(?P<format>(html|rdf|json|ttl))/$', PersonPhotosView.as_view()),
    url(r'^people/(?P<id>\d+)/photos/$', PersonPhotosView.as_view(), name='person-photos-view'),

    url(r'^people/add/$', AddPerson.as_view(), name="person-add"),
    url(r'^people/(?P<pk>\d+)/update/$', UpdatePerson.as_view(), name="person-update"),
    url(r'^people/(?P<person_id>\d+)/add/$', AddPerson.as_view(), name="person-add-person"),
    url(r'^people/suggest/$', SuggestPerson.as_view(), name="person-suggest"),
    url(r'^people/suggest/(?P<person_id>\d+)/thanks/$', SuggestPersonResponse.as_view(), name="person-suggest-response"),
    url(r'^people/(?P<pk>\d+)/approve/$', ApprovePerson.as_view(), name="person-approve"),
    url(r'^people/suggested/$', SuggestedPersonListView.as_view(), name="people-suggested-list"),

    url(r'^organisations/$', OrganisationListView.as_view(), name="organisation-list"),
    url(r'^organisations/results\.(?P<format>(html|rdf|json|ttl))/$', OrganisationListView.as_view()),
    url(r'^organisations/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', OrganisationView.as_view()),
    url(r'^organisations/(?P<id>\d+)/$', OrganisationView.as_view(), name='organisation-view'),

    url(r'^organisations/add/$', AddOrganisation.as_view(), name="organisation-add"),
    url(r'^organisations/(?P<pk>\d+)/update/$', UpdateOrganisation.as_view(), name="oranisation-update"),
    url(r'^organisations/add/(?P<entity_type>(person|personorganisation))/(?P<entity_id>\d+)/$', AddOrganisation.as_view(), name='organisation-add-entity'),
    url(r'^organisations/(?P<pk>\d+)/delete/$', DeleteOrganisation.as_view(), name='organisation-delete'),

    url(r'^people/names/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', AltNameView.as_view()),
    url(r'^people/names/(?P<id>\d+)/$', AltNameView.as_view(), name='altname-view'),
    url(r'^people/names/(?P<pk>\d+)/update/$', UpdateAltName.as_view(), name='altname-update'),
    url(r'^people/(?P<person_id>\d+)/names/add/$', AddAltName.as_view(), name='altname-add'),
    url(r'^people/names/(?P<pk>\d+)/delete/$', DeleteAltName.as_view(), name='altname-delete'),

    url(r'^people/ranks/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', RankView.as_view()),
    url(r'^people/ranks/(?P<id>\d+)/$', RankView.as_view(), name='rank-view'),
    url(r'^people/ranks/(?P<pk>\d+)/update/$', UpdateRank.as_view(), name='rank-update'),
    url(r'^people/(?P<person_id>\d+)/ranks/add/$', AddRank.as_view(), name='rank-add'),
    url(r'^people/ranks/(?P<pk>\d+)/delete/$', DeleteRank.as_view(), name='rank-delete'),

    url(r'^people/servicenumbers/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', ServiceNumberView.as_view()),
    url(r'^people/servicenumbers/(?P<id>\d+)/$', ServiceNumberView.as_view(), name='servicenumber-view'),
    url(r'^people/servicenumbers/(?P<pk>\d+)/update/$', UpdateServiceNumber.as_view(), name='servicenumber-update'),
    url(r'^people/(?P<person_id>\d+)/servicenumbers/add/$', AddServiceNumber.as_view(), name='servicenumber-add'),
    url(r'^people/servicenumbers/(?P<pk>\d+)/delete/$', DeleteServiceNumber.as_view(), name='servicenumber-delete'),

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

    url(r'^people/relationships/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', PersonRelationshipView.as_view()),
    url(r'^people/relationships/(?P<id>\d+)/$', PersonRelationshipView.as_view(), name='person-relationship-view'),
    url(r'^people/relationships/(?P<pk>\d+)/update/$', UpdatePersonAssociatedPerson.as_view(), name='persontoperson-update'),
    url(r'^people/(?P<person_id>\d+)/relationships/add/$', AddPersonAssociatedPerson.as_view(), name='persontoperson-add'),
    url(r'^people/relationships/(?P<pk>\d+)/delete/$', DeletePersonAssociatedPerson.as_view(), name='persontoperson-delete'),

    url(r'^people/memberships/(?P<pk>\d+)/update/$', UpdatePersonAssociatedOrganisation.as_view(), name='personorganisation-update'),
    url(r'^people/(?P<person_id>\d+)/memberships/add/$', AddPersonAssociatedOrganisation.as_view(), name='personorganisation-add'),
    url(r'^people/memberships/(?P<pk>\d+)/delete/$', DeletePersonAssociatedOrganisation.as_view(), name='personorganisation-delete'),

    url(r'^people/addresses/(?P<pk>\d+)/update/$', UpdatePersonAddress.as_view(), name='personaddress-update'),
    url(r'^people/(?P<person_id>\d+)/addresses/add/$', AddPersonAddress.as_view(), name='personaddress-add'),
    url(r'^people/addresses/(?P<pk>\d+)/delete/$', DeletePersonAddress.as_view(), name='personaddress-delete'),

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
    url(r'^places/(?P<letter>[a-zA-Z]{1})/$', PlaceListView.as_view(), name="place-alpha-list"),
    url(r'^places/(?P<letter>[a-zA-Z]{1})/results\.(?P<format>(html|rdf|json|ttl))/$', PlaceListView.as_view()),
    url(r'^places/(?P<id>\d+)/$', PlaceView.as_view(), name='place-view'),
    url(r'^places/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', PlaceView.as_view()),
    url(r'^places/(?P<pk>\d+)/update/$', UpdatePlace.as_view(), name='place-update'),
    url(r'^places/add/(?P<entity_type>(births|deaths|address))/(?P<entity_id>\d+)/$', AddPlace.as_view(), name='place-add-entity'),
    url(r'^places/add/$', AddPlace.as_view(), name='place-add'),

    url(r'^addresses/$', AddressListView.as_view(), name="address-list"),
    url(r'^addresses/results\.(?P<format>(html|rdf|json|ttl))/$', AddressListView.as_view()),
    url(r'^addresses/(?P<id>\d+)/$', AddressView.as_view(), name='address-view'),
    url(r'^addresses/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', AddressView.as_view()),
    url(r'^addresses/(?P<pk>\d+)/update/$', UpdateAddress.as_view(), name='address-update'),
    url(r'^addresses/add/$', AddAddress.as_view(), name='address-add'),
    url(r'^addresses/(?P<pk>\d+)/delete/$', DeleteAddress.as_view(), name='address-delete'),
    url(r'^addresses/add/(?P<entity_type>(person|personaddress))/(?P<entity_id>\d+)/$', AddAddress.as_view(), name='address-add-entity'),
)
urlpatterns += patterns('app.memorials.views',
    url(r'^memorials/$', MemorialListView.as_view(), name="memorial-list"),
    url(r'^memorials/results\.(?P<format>(html|rdf|json|ttl))/$', MemorialListView.as_view()),
    url(r'^memorials/(?P<id>\d+)\.(?P<format>(html|rdf|json|ttl))/$', MemorialView.as_view()),
    url(r'^memorials/(?P<id>\d+)/$', MemorialView.as_view(), name='memorial-view'),
    url(r'^memorials/(?P<id>\d+)/photos\.(?P<format>(html|rdf|json|ttl))/$', MemorialPhotosView.as_view()),
    url(r'^memorials/(?P<id>\d+)/photos/$', MemorialPhotosView.as_view(), name='memorial-photos-view'),
    url(r'^memorials/(?P<memorial_id>\d+)/names/results\.(?P<format>(html|rdf|json|ttl))/$', MemorialNamesView.as_view()),
    url(r'^memorials/(?P<memorial_id>\d+)/names/$', MemorialNamesView.as_view(), name='memorial-names-list'),
    url(r'^memorials/parts/(?P<part_id>\d+)/results\.(?P<format>(html|rdf|json|ttl))/$', MemorialPartNamesView.as_view()),
    url(r'^memorials/parts/(?P<part_id>\d+)/$', MemorialPartNamesView.as_view(), name='memorial-part-names-list'),
)
urlpatterns += patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    (r'^ckeditor/', include('ckeditor.urls')),
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
