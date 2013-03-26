# Create your views here.

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from app.linkeddata.views import LinkedDataView, LinkedDataListView, RDFSchema
from app.places.models import *
from app.places.forms import *


class PlaceView(LinkedDataView):
    model = Place
    path = '/places/%s'
    template_name = 'places/place'

    def make_graph(self, entity):
        namespaces = {}
        graph = Graph()
        schemas = RDFSchema.objects.all()
        for schema in schemas:
            namespace = Namespace(schema.uri)
            graph.bind(schema.prefix, namespace)
            namespaces[schema.prefix] = namespace
        host_ns = Namespace('http://%s' % (Site.objects.get_current().domain))
        this_person = URIRef(host_ns[entity.get_absolute_url()])
        graph.add((this_person, namespaces['rdf']['type'], namespaces['foaf']['Person']))
        graph.add((this_person, namespaces['rdfs']['label'], Literal(str(entity))))
        return graph


class PlaceListView(LinkedDataListView):
    model = Place
    path = '/places/results'
    template_name = 'places/places'

    def make_graph(self, entities):
        namespaces = {}
        graph = Graph()
        schemas = RDFSchema.objects.all()
        for schema in schemas:
            namespace = Namespace(schema.uri)
            graph.bind(schema.prefix, namespace)
            namespaces[schema.prefix] = namespace
        host_ns = Namespace('http://%s' % (Site.objects.get_current().domain))
        for entity in entities:
            this_person = URIRef(host_ns[entity.get_absolute_url()])
            graph.add((this_person, namespaces['rdf']['type'], namespaces['foaf']['Person']))
            graph.add((this_person, namespaces['rdfs']['label'], Literal(str(entity))))
        return graph


class AddPlace(CreateView):
    template_name = 'places/add_place.html'
    form_class = AddPlaceForm
    model = Place

    def get_initial(self):
        event_type = self.kwargs.get('event_type', None)
        event_id = self.kwargs.get('event_id', None)
        if event_type == 'births':
            initial = {'birth_event': event_id}
        elif event_type == 'deaths':
            initial = {'death_event': event_id}
        elif event_type == 'lifeevents':
            initial = {'life_event': event_id}
        else:
            initial = {}
        return initial

    def get_success_url(self):
        if self.event:
            event_type = self.event.__class__.__name__.lower()
            url = reverse_lazy('{}-update'.format(event_type), args=[self.event.id])
        else:
            url = reverse_lazy('place-view', args=[self.object.id])
        return url

    def form_valid(self, form):
        place = form.save(commit=False)
        place.added_by = self.request.user
        place.save()
        birth = form.cleaned_data.get('birth_event', None)
        death = form.cleaned_data.get('death_event', None)
        life_event = form.cleaned_data.get('life_event', None)
        if birth:
            event = birth
        elif death:
            event = death
        elif life_event:
            event = life_event
        else:
            event = None
        if event:
            event.location = place
            event.save()
            self.event = event
        return HttpResponseRedirect(self.get_success_url())


class UpdatePlace(UpdateView):
    template_name = 'people/add_place.html'
    form_class = AddPlaceForm
    model = Place


class DeletePlace(DeleteView):
    model = Place
    success_url = reverse_lazy('place-list')
