# Create your views here.

from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from app.linkeddata.views import LinkedDataView, LinkedDataListView, RDFSchema
from app.places.models import *
from app.places.forms import *
from app.memorials.models import *
from app.people.models import *


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
    path = '/places/{}results'
    template_name = 'places/places'
    browse_field = 'place_name'
    queryset = Place.objects.filter(merged_into__isnull=True)

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
        entity_type = self.kwargs.get('entity_type', None)
        entity_id = self.kwargs.get('entity_id', None)
        if entity_type == 'births':
            initial = {'birth_event': entity_id}
        elif entity_type == 'deaths':
            initial = {'death_event': entity_id}
        elif entity_type == 'lifeevents':
            initial = {'life_event': entity_id}
        elif entity_type == 'address':
            initial = {'address': entity_id}
        else:
            initial = {}
        return initial

    def get_success_url(self):
        if self.entity:
            entity_type = self.entity.__class__.__name__.lower()
            url = reverse_lazy('{}-update'.format(entity_type), args=[self.entity.id])
        else:
            url = reverse_lazy('place-view', args=[self.object.id])
        return url

    def form_valid(self, form):
        place = form.save(commit=False)
        place.added_by = self.request.user
        place.save()
        self.object = place
        birth = form.cleaned_data.get('birth_event', None)
        death = form.cleaned_data.get('death_event', None)
        life_event = form.cleaned_data.get('life_event', None)
        address = form.cleaned_data.get('address', None)
        if birth:
            entity = birth
            entity.location = place
        elif death:
            entity = death
            entity.location = place
        elif life_event:
            entity = life_event
            entity.location = place
        elif address:
            entity = address
            entity.place = place
        else:
            entity = None
        if entity:
            entity.save()
        self.entity = entity
        return HttpResponseRedirect(self.get_success_url())


class UpdatePlace(UpdateView):
    template_name = 'places/add_place.html'
    form_class = AddPlaceForm
    model = Place

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('place-update', args=[self.object.id])
        else:
            url = reverse_lazy('place-view', args=[self.object.id])
        return url


class DeletePlace(DeleteView):
    model = Place
    success_url = reverse_lazy('place-list')


class AddressView(LinkedDataView):
    model = Address
    path = '/addresses/%s'
    template_name = 'places/address'

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


class AddressListView(LinkedDataListView):
    model = Address
    path = '/addresses/results'
    template_name = 'places/addresses'

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


class AddAddress(CreateView):
    form_class = AddAddressForm
    model = Address

    def get_initial(self):
        entity_type = self.kwargs.get('entity_type', None)
        entity_id = self.kwargs.get('entity_id', None)
        if entity_type == 'person':
            initial = {'person': entity_id}
        elif entity_type == 'personaddress':
            initial = {'person_address': entity_id}
        else:
            initial = {}
        return initial

    def form_valid(self, form):
        address = form.save(commit=False)
        address.added_by = self.request.user
        address.save()
        self.object = address
        person = form.cleaned_data.get('person', None)
        person_address = form.cleaned_data.get('person_address', None)
        if person:
            pa = PersonAddress.objects.create(
                person=person,
                address=address,
                added_by=self.request.user
            )
            self.entity = pa
        elif person_address:
            person_address.address = address
            person_address.save()
            self.entity = person_address
        else:
            self.entity = None
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.entity:
            url = reverse_lazy('personaddress-update', args=[self.entity.id])
        else:
            url = reverse_lazy('address-update', args=[self.object.id, ])
        return url


class UpdateAddress(UpdateView):
    form_class = AddAddressForm
    model = Address

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('address-update', args=[self.object.id])
        else:
            url = reverse_lazy('address-view', args=[self.object.id])
        return url


class DeleteAddress(DeleteView):
    model = Address
    success_url = reverse_lazy('address-list')


class MosmanStreetView(LinkedDataView):
    model = MosmanStreet
    path = '/mosmanstreets/%s'
    template_name = 'places/mosmanstreet'

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


class MosmanStreetListView(LinkedDataListView):
    model = MosmanStreet
    path = '/mosmanstreets/results'
    template_name = 'places/mosmanstreets'

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


class PlaceMergeView(FormView):
    template_name = 'places/place_merge_form.html'
    form_class = PlaceMergeForm

    def get_initial(self):
        id = self.kwargs.get('id', None)
        initial = {'merge_record': id}
        return initial

    def form_valid(self, form):
        merge_record = form.cleaned_data['merge_record']
        master_record = form.cleaned_data['master_record']
        # Find all properties of merged record and update
        for address in Address.objects.filter(place=merge_record):
            address.place = master_record
            address.save()
        for burial in Death.objects.filter(burial_place=merge_record):
            burial.burial_place = master_record
            burial.save()
        for birth in Birth.objects.filter(location=merge_record):
            birth.location = master_record
            birth.save()
        for death in Death.objects.filter(location=merge_record):
            death.location = master_record
            death.save()
        for event in EventLocation.objects.filter(location=merge_record):
            event.location = master_record
            event.save()
        for memorial in MemorialAssociatedPlace.objects.filter(place=merge_record):
            memorial.place = master_record
            memorial.save()
        for memorial in Memorial.objects.filter(location=merge_record):
            memorial.location = master_record
            memorial.save()
        for source in merge_record.sources.all():
            master_record.sources.add(source)
            master_record.save()
        merge_record.sources.clear()
        merge_record.merged_into = master_record
        merge_record.save()
        self.redirect = master_record
        return super(PlaceMergeView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('place-view', args=[self.redirect.id])
