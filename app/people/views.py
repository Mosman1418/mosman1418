# Create your views here.
from django.shortcuts import render_to_response, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sites.models import Site
from django.views.generic.edit import FormView
import json
from django.http import HttpResponse, HttpResponseRedirect
from guardian.decorators import permission_required
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.contenttypes.models import ContentType
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from calendar import monthrange
import re
from urllib2 import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup
import mechanize

from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from guardian.shortcuts import assign

from app.linkeddata.views import LinkedDataView, LinkedDataListView, RDFSchema
from app.people.models import *
from app.people.forms import *


TROVE_API_KEY = 'ierj9cpsh7f5u7kg'


def check_date(date, type):
    month_known = True
    day_known = True
    year, month, day = date.split('-')
    if int(month) == 0:
        month_known = False
        day_known = False
        if type == 'start':
            month = '01'
            day = '01'
        elif type == 'end':
            month = '12'
            day = '31'
    else:
        if int(day) == 0:
            day_known = False
            if type == 'start':
                day = '01'
            elif type == 'end':
                day = monthrange(int(year), int(month))[1]
    return {'date': '%s-%s-%s' % (year, month, day), 'month_known': month_known, 'day_known': day_known}


def get_naa_details(barcode):
    br = mechanize.Browser()
    br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]
    br.set_handle_robots(False)
    url = 'http://www.naa.gov.au/cgi-bin/Search?O=I&Number=%s' % barcode
    response1 = br.open(url)
    # Recordsearch returns a page with a form that submits on page load.
    # Have to make sure the session id is submitted with the form.
    # Extract the session id.
    session_id = re.search(r"value={(.*)}", response1.read()).group(1)
    br.select_form(name="t")
    br.form.set_all_readonly(False)
    # Add session id to the form.
    br.form['NAASessionID'] = '{%s}' % session_id
    response2 = br.submit()
    soup = BeautifulSoup(response2.read())
    try:
        series = unicode(soup.find('div', text='Series number').parent.next_sibling.next_sibling.a.string)
        control = unicode(soup.find('div', text='Control symbol').parent.next_sibling.next_sibling.string)
        title = unicode(soup.find('div', text='Title').parent.next_sibling.next_sibling.string)
    except AttributeError:
        raise Http404
    return {'series': series, 'control': control, 'title': title}


def prepare_date(date, month_known, day_known):
    year, month, day = date.isoformat().split('-')
    if month_known == False:
        month = '0'
    if day_known == False:
        day = '0'
    return '%s-%s-%s' % (year, month, day)


class PersonView(LinkedDataView):
    model = Person
    path = '/people/%s'
    template_name = 'people/person'

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
        graph.add((this_person, namespaces['foaf']['name'], Literal(str(entity))))
        graph.add((this_person, namespaces['foaf']['familyName'], Literal(entity.family_name)))
        if entity.other_names:
            graph.add((this_person, namespaces['foaf']['givenName'], Literal(entity.other_names)))
        if entity.memorialname_set.all():
            for memorialname in entity.memorialname_set.all():
                graph.add((this_person, namespaces['graves']['commemorated_by'], URIRef(host_ns[memorialname.memorial.get_absolute_url()])))
        for story in entity.stories.all():
            graph.add((this_person, namespaces['foaf']['page'], URIRef(host_ns[story.get_absolute_url()])))
        return graph


class PersonListView(LinkedDataListView):
    model = Person
    path = '/people/results'
    template_name = 'people/people'
    queryset = Person.objects.filter(status='confirmed')

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


class SuggestedPersonListView(PermissionRequiredMixin, ListView):
    model = Person
    template_name = 'people/people.html'
    queryset = Person.objects.filter(status='pending')
    context_object_name = 'content'
    permission_required = 'people.approve_person'

    def get_context_data(self, **kwargs):
        context = super(SuggestedPersonListView, self).get_context_data(**kwargs)
        context['status'] = 'pending'
        return context


class AltNameView(LinkedDataView):
    model = AlternativePersonName
    path = '/people/names/%s'
    template_name = 'people/altname'

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


class BirthView(LinkedDataView):
    model = Birth
    path = '/people/births/%s'
    template_name = 'people/birth'

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


class DeathView(LinkedDataView):
    model = Death
    path = '/people/deaths/%s'
    template_name = 'people/death'

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


class LifeEventView(LinkedDataView):
    model = LifeEvent
    path = '/people/events/%s'
    template_name = 'people/life_event'

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


class StoryView(LinkedDataView):
    model = PeopleStory
    path = '/stories/%s'
    template_name = 'people/story'

    def make_graph(self, entity):
        namespaces = {}
        graph = Graph()
        schemas = RDFSchema.objects.all()
        for schema in schemas:
            namespace = Namespace(schema.uri)
            graph.bind(schema.prefix, namespace)
            namespaces[schema.prefix] = namespace
        host_ns = Namespace('http://%s' % (Site.objects.get_current().domain))
        this_entity = URIRef(host_ns[entity.get_absolute_url()])
        graph.add((this_entity, namespaces['rdf']['type'], namespaces['bibo']['Note']))
        graph.add((this_entity, namespaces['rdfs']['label'], Literal(str(entity))))
        graph.add((this_entity, namespaces['dc']['title'], Literal(str(entity))))
        graph.add((this_entity, namespaces['rdf']['value'], Literal(entity.text)))
        graph.add((this_entity, namespaces['dc']['creator'], Literal(entity.created_by.username)))
        for person in entity.person_set.all():
            graph.add((this_entity, namespaces['foaf']['topic'], URIRef(host_ns[person.get_absolute_url()])))
        return graph


class StoryListView(LinkedDataListView):
    model = PeopleStory
    path = '/stories/results'
    template_name = 'people/stories'

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
            this_entity = URIRef(host_ns[entity.get_absolute_url()])
            graph.add((this_entity, namespaces['rdf']['type'], namespaces['bibo']['Note']))
            graph.add((this_entity, namespaces['rdfs']['label'], Literal(str(entity))))
        return graph


class ImageView(LinkedDataView):
    model = PeopleImage
    path = '/images/%s'
    template_name = 'people/image'

    def make_graph(self, entity):
        namespaces = {}
        graph = Graph()
        schemas = RDFSchema.objects.all()
        for schema in schemas:
            namespace = Namespace(schema.uri)
            graph.bind(schema.prefix, namespace)
            namespaces[schema.prefix] = namespace
        host_ns = Namespace('http://%s' % (Site.objects.get_current().domain))
        this_entity = URIRef(host_ns[entity.get_absolute_url()])
        graph.add((this_entity, namespaces['rdf']['type'], namespaces['foaf']['Image']))
        graph.add((this_entity, namespaces['rdfs']['label'], Literal(str(entity))))
        graph.add((this_entity, namespaces['dc']['title'], Literal(str(entity))))
        for person in entity.person_set.all():
            graph.add((this_entity, namespaces['foaf']['depicts'], URIRef(host_ns[person.get_absolute_url()])))
        return graph


class ImageListView(LinkedDataListView):
    model = PeopleImage
    path = '/images/results'
    template_name = 'people/images'

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
            this_entity = URIRef(host_ns[entity.get_absolute_url()])
            graph.add((this_entity, namespaces['rdf']['type'], namespaces['foaf']['Image']))
            graph.add((this_entity, namespaces['rdfs']['label'], Literal(str(entity))))
        return graph


class OrganisationView(LinkedDataView):
    model = Organisation
    path = '/organisations/%s'
    template_name = 'people/organisation'

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


class OrganisationListView(LinkedDataListView):
    model = Organisation
    path = '/organisations/results'
    template_name = 'people/organisations'

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


class RankView(LinkedDataView):
    model = Rank
    path = '/people/ranks/%s'
    template_name = 'people/rank'

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


class ServiceNumberView(LinkedDataView):
    model = ServiceNumber
    path = '/people/servicenumbers/%s'
    template_name = 'people/servicenumber'

    def make_graph(self, entity):
        namespaces = {}
        graph = Graph()
        schemas = RDFSchema.objects.all()
        for schema in schemas:
            namespace = Namespace(schema.uri)
            graph.bind(schema.prefix, namespace)
            namespaces[schema.prefix] = namespace
        host_ns = Namespace('http://%s' % (Site.objects.get_current().domain))
        this_person = URIRef(host_ns[entity.person.get_absolute_url()])
        graph.add((this_person, namespaces['rdf']['type'], namespaces['foaf']['Person']))
        graph.add((this_person, namespaces['dc']['identifier'], Literal(str(entity.service_number))))
        return graph


class PersonRelationshipView(LinkedDataView):
    model = PersonAssociatedPerson
    path = '/people/relationships/%s'
    template_name = 'people/relationship'

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


class SuggestPerson(CreateView):
    '''
    A logged-in user can suggest a service person for inclusion.
    The entry is marked "pending" until an admin user inspects it.
    '''
    form_class = AddPersonForm
    model = Person

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(SuggestPerson, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.form = form
        person = form.save(commit=False)
        person.added_by = self.request.user
        person.status = 'pending'
        person.save()
        self.object = person
        assign('people.change_person', self.request.user, person)
        assign('people.delete_person', self.request.user, person)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(SuggestPerson, self).get_context_data(**kwargs)
        context['status'] = 'pending'
        return context

    def get_success_url(self):
        return reverse_lazy('person-suggest-response', args=[self.object.id])


class SuggestPersonResponse(PermissionRequiredMixin, TemplateView):
    '''
    Thank user for suggested person.
    Provide update link to add more details.
    '''
    template_name = 'people/suggest_person_thanks.html'
    permission_required = 'people.add_person'

    def get_context_data(self, **kwargs):
        context = super(SuggestPersonResponse, self).get_context_data(**kwargs)
        person_id = self.kwargs.get('person_id', None)
        if person_id:
            context['person'] = Person.objects.get(id=person_id)
        return context


class AddPerson(CreateView):
    form_class = AddPersonForm
    model = Person

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddPerson, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.form = form
        person = form.save(commit=False)
        person.added_by = self.request.user
        person.status = 'non-service'
        person.save()
        assign('people.change_person', self.request.user, person)
        assign('people.delete_person', self.request.user, person)
        related_person = form.cleaned_data.get('related_person', None)
        if related_person:
            related_person.associated_person = person
            related_person.save()
        source = form.cleaned_data.get('source', None)
        creator_type = form.cleaned_data.get('creator_type', None)
        if source and creator_type:
            role = SourceRole.objects.get(label=creator_type)
            creator, created = SourcePerson.objects.get_or_create(
                        person=person,
                        source=source,
                        role=role
                    )
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        initial = {}
        person_id = self.kwargs.get('person_id', None)
        if person_id:
            initial['related_person'] = person_id
        source_id = self.kwargs.get('source_id', None)
        creator_type = self.kwargs.get('creator_type', None)
        if source_id and creator_type:
            initial['source'] = source_id
            initial['creator_type'] = creator_type
        return initial

    def get_success_url(self):
        related_person = self.form.cleaned_data.get('related_person', None)
        source = self.form.cleaned_data.get('source', None)
        if related_person:
            url = reverse_lazy('persontoperson-update', args=[related_person.id])
        elif source:
            url = reverse_lazy('source-update', args=[source.id])
        else:
            url = reverse_lazy('person-update', args=[self.object.id])
        print url
        return url


class UpdatePerson(PermissionRequiredMixin, UpdateView):
    form_class = UpdatePersonForm
    model = Person
    permission_required = 'people.change_person'

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month_known'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day_known'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['birth_earliest_date'] = self.prepare_date('birth_earliest_date')
        initial['birth_latest_date'] = self.prepare_date('birth_latest_date')
        initial['death_earliest_date'] = self.prepare_date('death_earliest_date')
        initial['death_latest_date'] = self.prepare_date('death_latest_date')
        return initial

    def form_valid(self, form):
        person = form.save(commit=False)
        person.save()
        return HttpResponseRedirect(reverse('person-view', args=[person.id]))


class ApprovePerson(PermissionRequiredMixin, UpdateView):
    model = Person
    form_class = ApprovePersonForm
    permission_required = 'people.approve_person'
    template_name = 'people/person_approve.html'


class DeletePerson(PermissionRequiredMixin, DeleteView):
    model = Person
    success_url = reverse_lazy('people-list')
    permission_required = 'people.delete_person'


class AddAltName(CreateView):
    model = AlternativePersonName
    form_class = AddAltNameForm

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddAltName, self).dispatch(*args, **kwargs)

    def get_initial(self):
        person_id = self.kwargs.get('person_id', None)
        initial = {'person': person_id}
        return initial

    def form_valid(self, form):
        altname = form.save(commit=False)
        altname.added_by = self.request.user
        altname.save()
        assign('people.change_alternativepersonname', self.request.user, altname)
        assign('people.delete_alternativepersonname', self.request.user, altname)
        return HttpResponseRedirect(reverse('altname-update', args=[altname.id]))


class UpdateAltName(PermissionRequiredMixin, UpdateView):
    model = AlternativePersonName
    form_class = AddAltNameForm
    permission_required = 'people.change_alternativepersonname'

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('altname-update', args=[self.object.id])
        else:
            url = reverse_lazy('person-update', args=[self.object.person.id])
        return url


class DeleteAltName(PermissionRequiredMixin, DeleteView):
    model = AlternativePersonName
    permission_required = 'people.delete_alternativepersonname'

    def delete(self, request, *args, **kwargs):
        self.person_pk = self.get_object().person.pk
        return super(DeleteAltName, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('person-update', args=[self.person_pk])


class AddLifeEvent(CreateView):
    form_class = AddLifeEventForm
    model = LifeEvent

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddLifeEvent, self).dispatch(*args, **kwargs)

    def get_initial(self):
        person_id = self.kwargs.get('person_id', None)
        initial = {'person': person_id}
        return initial

    def form_valid(self, form):
        event = form.save(commit=False)
        event.added_by = self.request.user
        event.save()
        assign('people.change_lifeevent', self.request.user, event)
        assign('people.delete_lifeevent', self.request.user, event)
        return HttpResponseRedirect(reverse('lifeevent-update', args=[event.id]))


class UpdateLifeEvent(PermissionRequiredMixin, UpdateView):
    form_class = AddLifeEventForm
    model = LifeEvent
    permission_required = 'people.change_lifeevent'

    def form_valid(self, form):
        event = form.save(commit=False)
        event.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('lifeevent-update', args=[self.object.id])
        else:
            url = reverse_lazy('lifeevent-view', args=[self.object.id])
        return url

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['start_earliest_date'] = self.prepare_date('start_earliest_date')
        initial['start_latest_date'] = self.prepare_date('start_latest_date')
        initial['end_earliest_date'] = self.prepare_date('end_earliest_date')
        initial['end_latest_date'] = self.prepare_date('end_latest_date')
        return initial


class DeleteLifeEvent(PermissionRequiredMixin, DeleteView):
    model = LifeEvent
    template_name = 'people/confirm_delete.html'
    permission_required = 'people.delete_lifeevent'

    def delete(self, request, *args, **kwargs):
        self.person_pk = self.get_object().person.pk
        return super(DeleteLifeEvent, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('person-update', args=[self.person_pk])


class AddEventLocation(CreateView):
    form_class = AddEventLocationForm
    model = EventLocation

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddEventLocation, self).dispatch(*args, **kwargs)

    def get_initial(self):
        event_id = self.kwargs.get('event_id', None)
        initial = {'lifeevent': event_id}
        return initial

    def form_valid(self, form):
        location = form.save(commit=False)
        location.added_by = self.request.user
        location.save()
        assign('people.change_eventlocation', self.request.user, location)
        assign('people.delete_eventlocation', self.request.user, location)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('eventlocation-update', args=[self.object.id])


class UpdateEventLocation(PermissionRequiredMixin, UpdateView):
    form_class = AddEventLocationForm
    model = EventLocation
    permission_required = 'people.change_eventlocation'

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('eventlocation-update', args=[self.object.id])
        else:
            url = reverse_lazy('lifeevent-update', args=[self.object.lifeevent.id])
        return url


class DeleteEventLocation(PermissionRequiredMixin, DeleteView):
    model = EventLocation
    template_name = 'people/confirm_delete.html'
    permission_required = 'people.delete_eventlocation'

    def delete(self, request, *args, **kwargs):
        self.lifeevent_id = self.get_object().lifeevent.id
        return super(DeleteEventLocation, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('lifeevent-update', args=[self.lifeevent_id])


class AddBirth(CreateView):
    form_class = AddBirthForm
    model = Birth

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddBirth, self).dispatch(*args, **kwargs)

    def get_initial(self):
        person_id = self.kwargs.get('person_id', None)
        initial = {'person': person_id}
        return initial

    def form_valid(self, form):
        birth = form.save(commit=False)
        birth.added_by = self.request.user
        birth.save()
        assign('people.change_birth', self.request.user, birth)
        assign('people.delete_birth', self.request.user, birth)
        return HttpResponseRedirect(reverse('birth-update', args=[birth.id]))


class UpdateBirth(PermissionRequiredMixin, UpdateView):
    form_class = AddBirthForm
    model = Birth
    permission_required = 'people.change_birth'

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('birth-update', args=[self.object.id])
        else:
            url = reverse_lazy('person-update', args=[self.object.person.id])
        return url

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['start_earliest_date'] = self.prepare_date('start_earliest_date')
        initial['start_latest_date'] = self.prepare_date('start_latest_date')
        return initial


class DeleteBirth(PermissionRequiredMixin, DeleteView):
    model = Birth
    permission_required = 'people.delete_birth'

    def delete(self, request, *args, **kwargs):
        self.person_pk = self.get_object().person.pk
        return super(DeleteBirth, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('person-update', args=[self.person_pk])


class AddDeath(CreateView):
    form_class = AddDeathForm
    model = Death

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddDeath, self).dispatch(*args, **kwargs)

    def get_initial(self):
        person_id = self.kwargs.get('person_id', None)
        initial = {'person': person_id}
        return initial

    def form_valid(self, form):
        death = form.save(commit=False)
        death.added_by = self.request.user
        death.save()
        assign('people.change_death', self.request.user, death)
        assign('people.delete_death', self.request.user, death)
        return HttpResponseRedirect(reverse('death-update', args=[death.id]))


class UpdateDeath(PermissionRequiredMixin, UpdateView):
    form_class = AddDeathForm
    model = Death
    permission_required = 'people.change_death'

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('death-update', args=[self.object.id])
        else:
            url = reverse_lazy('person-view', args=[self.object.person.id])
        return url

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['start_earliest_date'] = self.prepare_date('start_earliest_date')
        initial['start_latest_date'] = self.prepare_date('start_latest_date')
        return initial


class DeleteDeath(PermissionRequiredMixin, DeleteView):
    model = Death
    permission_required = 'people.delete_death'

    def delete(self, request, *args, **kwargs):
        self.person_pk = self.get_object().person.pk
        return super(DeleteDeath, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('person-update', args=[self.person_pk])


class AddOrganisation(CreateView):
    form_class = AddOrganisationForm
    model = Organisation

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddOrganisation, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.form = form
        org = form.save(commit=False)
        org.added_by = self.request.user
        org.save()
        assign('people.change_organisation', self.request.user, org)
        assign('people.delete_organisation', self.request.user, org)
        person = form.cleaned_data.get('person', None)
        associated_person = form.cleaned_data.get('associated_person', None)
        if person:
            person_org = PersonAssociatedOrganisation.objects.create(
                    person=person,
                    organisation=org,
                    added_by=self.request.user
                )
            self.entity = person_org
        elif associated_person:
            associated_person.organisation = org
            associated_person.save()
            self.entity = associated_person
        else:
            self.entity = None
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        entity_type = self.kwargs.get('entity_type', None)
        entity_id = self.kwargs.get('entity_id', None)
        if entity_type == 'person':
            initial = {'person': entity_id}
        elif entity_type == 'personaddress':
            initial = {'associated_person': entity_id}
        else:
            initial = {}
        return initial

    def get_success_url(self):
        if self.entity:
            url = reverse_lazy('personorganisation-update', args=[self.entity.id])
        else:
            url = reverse_lazy('organisation-update', args=[self.object.id, ])
        return url


class UpdateOrganisation(PermissionRequiredMixin, UpdateView):
    form_class = AddOrganisationForm
    model = Organisation
    permission_required = 'people.change_organisation'

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['start_earliest_date'] = self.prepare_date('start_earliest_date')
        initial['end_earliest_date'] = self.prepare_date('end_earliest_date')
        return initial

    def form_valid(self, form):
        org = form.save(commit=False)
        org.save()
        return HttpResponseRedirect(reverse('organisation-view', args=[person.id]))


class DeleteOrganisation(PermissionRequiredMixin, DeleteView):
    model = Organisation
    template_name = 'people/confirm_delete.html'
    success_url = reverse_lazy('organisation-list')
    permission_required = 'people.delete_organisation'


class AddPersonAssociatedPerson(CreateView):
    model = PersonAssociatedPerson
    form_class = AddAssociatedPersonForm

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddPersonAssociatedPerson, self).dispatch(*args, **kwargs)

    def get_initial(self):
        person_id = self.kwargs.get('person_id', None)
        initial = {'person': person_id}
        return initial

    def form_valid(self, form):
        assoc = form.save(commit=False)
        assoc.added_by = self.request.user
        assoc.save()
        assign('people.change_personassociatedperson', self.request.user, assoc)
        assign('people.delete_personassociatedperson', self.request.user, assoc)
        return HttpResponseRedirect(reverse('persontoperson-update', args=[assoc.id]))


class UpdatePersonAssociatedPerson(PermissionRequiredMixin, UpdateView):
    model = PersonAssociatedPerson
    form_class = AddAssociatedPersonForm
    permission_required = 'people.change_personassociatedperson'

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['start_earliest_date'] = self.prepare_date('start_earliest_date')
        initial['end_earliest_date'] = self.prepare_date('end_earliest_date')
        return initial

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('persontoperson-update', args=[self.object.id])
        else:
            url = reverse_lazy('person-update', args=[self.object.person.id])
        return url


class DeletePersonAssociatedPerson(PermissionRequiredMixin, DeleteView):
    model = PersonAssociatedPerson
    template_name = 'people/confirm_delete.html'
    permission_required = 'people.delete_personassociatedperson'

    def delete(self, request, *args, **kwargs):
        self.person_pk = self.get_object().person.pk
        return super(DeletePersonAssociatedPerson, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('person-update', args=[self.person_pk])


class AddPersonAssociatedOrganisation(CreateView):
    model = PersonAssociatedOrganisation
    form_class = AddAssociatedOrganisationForm

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddPersonAssociatedOrganisation, self).dispatch(*args, **kwargs)

    def get_initial(self):
        person_id = self.kwargs.get('person_id', None)
        initial = {'person': person_id}
        return initial

    def form_valid(self, form):
        assoc = form.save(commit=False)
        assoc.added_by = self.request.user
        assoc.save()
        assign('people.change_personassociatedorganisation', self.request.user, assoc)
        assign('people.delete_personassociatedorganisation', self.request.user, assoc)
        return HttpResponseRedirect(reverse('personorganisation-update', args=[assoc.id]))


class UpdatePersonAssociatedOrganisation(PermissionRequiredMixin, UpdateView):
    model = PersonAssociatedOrganisation
    form_class = AddAssociatedOrganisationForm
    permission_required = 'people.change_personassociatedorganisation'

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['start_earliest_date'] = self.prepare_date('start_earliest_date')
        initial['end_earliest_date'] = self.prepare_date('end_earliest_date')
        return initial

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('personorganisation-update', args=[self.object.id])
        else:
            url = reverse_lazy('person-update', args=[self.object.person.id])
        return url


class DeletePersonAssociatedOrganisation(PermissionRequiredMixin, DeleteView):
    model = PersonAssociatedOrganisation
    template_name = 'people/confirm_delete.html'
    permission_required = 'people.delete_personassociatedorganisation'

    def delete(self, request, *args, **kwargs):
        self.person_pk = self.get_object().person.pk
        return super(DeletePersonAssociatedOrganisation, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('person-update', args=[self.person_pk])


class AddPersonAddress(CreateView):
    model = PersonAddress
    form_class = AddPersonAddressForm

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_person'))
    def dispatch(self, *args, **kwargs):
        return super(AddPersonAddress, self).dispatch(*args, **kwargs)

    def get_initial(self):
        person_id = self.kwargs.get('person_id', None)
        initial = {'person': person_id}
        return initial

    def form_valid(self, form):
        address = form.save(commit=False)
        address.added_by = self.request.user
        address.save()
        assign('people.change_personaddress', self.request.user, address)
        assign('people.delete_personaddress', self.request.user, address)
        return HttpResponseRedirect(reverse('personaddress-update', args=[address.id]))


class UpdatePersonAddress(PermissionRequiredMixin, UpdateView):
    model = PersonAddress
    form_class = AddPersonAddressForm
    permission_required = 'people.change_personaddress'

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['start_earliest_date'] = self.prepare_date('start_earliest_date')
        initial['end_earliest_date'] = self.prepare_date('end_earliest_date')
        return initial

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('personaddress-update', args=[self.object.id])
        else:
            url = reverse_lazy('person-update', args=[self.object.person.id])
        return url


class DeletePersonAddress(PermissionRequiredMixin, DeleteView):
    model = PersonAddress
    template_name = 'people/confirm_delete.html'
    permission_required = 'people.delete_personaddress'

    def delete(self, request, *args, **kwargs):
        self.person_pk = self.get_object().person.pk
        return super(DeletePersonAddress, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('person-update', args=[self.person_pk])


class AddRank(CreateView):
    model = Rank
    form_class = AddRankForm

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_rank'))
    def dispatch(self, *args, **kwargs):
        return super(AddRank, self).dispatch(*args, **kwargs)

    def get_initial(self):
        person_id = self.kwargs.get('person_id', None)
        initial = {'person': person_id}
        return initial

    def form_valid(self, form):
        rank = form.save(commit=False)
        rank.added_by = self.request.user
        rank.save()
        assign('people.change_rank', self.request.user, rank)
        assign('people.delete_rank', self.request.user, rank)
        return HttpResponseRedirect(reverse('person-update', args=[rank.person.id]))


class UpdateRank(PermissionRequiredMixin, UpdateView):
    model = Rank
    form_class = AddRankForm
    permission_required = 'people.change_rank'

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['start_earliest_date'] = self.prepare_date('start_earliest_date')
        initial['end_earliest_date'] = self.prepare_date('end_earliest_date')
        return initial

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('rank-update', args=[self.object.id])
        else:
            url = reverse_lazy('person-update', args=[self.object.person.id])
        return url


class DeleteRank(PermissionRequiredMixin, DeleteView):
    model = Rank
    template_name = 'people/confirm_delete.html'
    permission_required = 'people.delete_rank'

    def delete(self, request, *args, **kwargs):
        self.person_pk = self.get_object().person.pk
        return super(DeleteRank, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('person-update', args=[self.person_pk])


class AddServiceNumber(CreateView):
    model = ServiceNumber
    form_class = AddServiceNumberForm

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_servicenumber'))
    def dispatch(self, *args, **kwargs):
        return super(AddServiceNumber, self).dispatch(*args, **kwargs)

    def get_initial(self):
        person_id = self.kwargs.get('person_id', None)
        initial = {'person': person_id}
        return initial

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.added_by = self.request.user
        obj.save()
        assign('people.change_servicenumber', self.request.user, obj)
        assign('people.delete_servicenumber', self.request.user, obj)
        return HttpResponseRedirect(reverse('servicenumber-update', args=[obj.id]))


class UpdateServiceNumber(PermissionRequiredMixin, UpdateView):
    model = ServiceNumber
    form_class = AddServiceNumberForm
    permission_required = 'people.change_servicenumber'

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('servicenumber-update', args=[self.object.id])
        else:
            url = reverse_lazy('person-update', args=[self.object.person.id])
        return url


class DeleteServiceNumber(PermissionRequiredMixin, DeleteView):
    model = ServiceNumber
    template_name = 'people/confirm_delete.html'
    permission_required = 'people.delete_servicenumber'

    def delete(self, request, *args, **kwargs):
        self.person_pk = self.get_object().person.pk
        return super(DeleteServiceNumber, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('person-update', args=[self.person_pk])


@permission_required('people.add_peoplestory', accept_global_perms=True)
def add_story(request, id=None, entity_type=None):
    if request.method == 'POST':
        form = AddStoryForm(request.POST)
        if form.is_valid():
            people = form.cleaned_data['people']
            organisations = form.cleaned_data['organisations']
            story = form.save(commit=False)
            story.created_by = request.user
            story.save()
            for person in people:
                story.person_set.add(Person.objects.get(id=int(person)))
            for organisation in organisations:
                story.person_set.add(Organisation.objects.get(id=int(organisation)))
            story.save()
            assign('people.change_peoplestory', request.user, story)
            assign('people.delete_peoplestory', request.user, story)
            return HttpResponseRedirect(reverse('view_story', args=[story.id]))
        else:
            people = Person.objects.filter(id__in=request.POST.getlist('people'))
            people_ids = [person.id for person in people]
            form.initial['people'] = people_ids
            organisations = Person.objects.filter(id__in=request.POST.getlist('organisations'))
            organisations_ids = [organisation.id for organisation in organisations]
            form.initial['organisations'] = organisations_ids
    else:
        form = AddStoryForm()
        people = None
        organisations = None
        if entity_type:
            content_type = ContentType.objects.get(app_label="people", model=entity_type)
            entity = content_type.get_object_for_this_type(pk=id)
            entities = [entity]
            entity_ids = [entity.id]
        if entity_type == 'person':
            form.initial['people'] = entity_ids
            people = entities
        elif entity_type == 'organisation':
            form.initial['organisations'] = entity_ids
            organisations = entities
    return render(request, 'people/add_story.html', {
        'form': form, 'people': people, 'organisations': organisations, 'story_id': None
    })


@permission_required('people.change_peoplestory', (PeopleStory, 'id', 'id'))
def edit_story(request, id):
    story = get_object_or_404(PeopleStory, id=id)
    if request.method == 'POST':
        form = AddStoryForm(request.POST, instance=story)
        if form.is_valid():
            people = form.cleaned_data['people']
            organisations = form.cleaned_data['organisations']
            form.save(commit=False)
            story.person_set.clear()
            story.organisation_set.clear()
            for person in people:
                story.person_set.add(Person.objects.get(id=person))
            for organisation in organisations:
                story.person_set.add(Organisation.objects.get(id=int(organisation)))
            story.save()
            return HttpResponseRedirect(reverse('view_story', args=[id]))
        else:
            people = Person.objects.filter(id__in=request.POST.getlist('people'))
            people_ids = [person.id for person in people]
            form.initial['people'] = people_ids
            organisations = Person.objects.filter(id__in=request.POST.getlist('organisations'))
            organisations_ids = [organisation.id for organisation in organisations]
            form.initial['organisations'] = organisations_ids
    else:
        people = story.person_set.all()
        people_ids = [person.id for person in people]
        organisations = story.organisation_set.all()
        organisations_ids = [organisation.id for organisation in organisations]
        if story.earliest_date:
            earliest_date = prepare_date(story.earliest_date, story.earliest_month_known, story.earliest_day_known)
        else:
            earliest_date = None
        if story.latest_date:
            latest_date = prepare_date(story.latest_date, story.latest_month_known, story.latest_day_known)
        else:
            latest_date = None
        form = AddStoryForm(instance=story, initial={
            'people': people_ids,
            'organisations': organisations_ids,
            'earliest_date': earliest_date,
            'latest_date': latest_date})
    return render(request, 'people/add_story.html', {
        'form': form, 'people': people, 'organisations': organisations, 'story_id': id
    })


@permission_required('people.delete_peoplestory', (PeopleStory, 'id', 'id'))
def delete_story(request, id=None):
    if request.method == 'POST':
        form = DeleteStoryForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            PeopleStory.objects.get(id=id).delete()
            return HttpResponseRedirect(reverse('people_list'))
    else:
        story = PeopleStory.objects.get(id=id)
        form = DeleteStoryForm(initial={'id': id})
    return render(request, 'people/delete_story.html', {
        'form': form, 'story': story
    })


@permission_required('people.add_peopleimage', accept_global_perms=True)
def add_image(request, id=None, entity_type=None):
    if request.method == 'POST':
        form = AddImageForm(request.POST, request.FILES)
        if form.is_valid():
            people = form.cleaned_data['people']
            organisations = form.cleaned_data['organisations']
            image = form.save(commit=False)
            image.added_by = request.user
            image.save()
            for person in people:
                image.person_set.add(Person.objects.get(id=int(person)))
            for organisation in organisations:
                image.person_set.add(Organisation.objects.get(id=int(organisation)))
            image.save()
            assign('people.change_peopleimage', request.user, image)
            assign('people.delete_peopleimage', request.user, image)
            return HttpResponseRedirect(reverse('view_image', args=[image.id]))
        else:
            people = Person.objects.filter(id__in=request.POST.getlist('people'))
            people_ids = [person.id for person in people]
            form.initial['people'] = people_ids
            organisations = Person.objects.filter(id__in=request.POST.getlist('organisations'))
            organisations_ids = [organisation.id for organisation in organisations]
            form.initial['organisations'] = organisations_ids
    else:
        form = AddImageForm()
        people = None
        organisations = None
        if entity_type:
            content_type = ContentType.objects.get(app_label="people", model=entity_type)
            entity = content_type.get_object_for_this_type(pk=id)
            entities = [entity]
            entity_ids = [entity.id]
        if entity_type == 'person':
            form.initial['people'] = entity_ids
            people = entities
        elif entity_type == 'organisation':
            form.initial['organisations'] = entity_ids
            organisations = entities
    return render(request, 'people/add_image.html', {
        'form': form, 'people': people, 'organisations': organisations, 'image_id': None
    })


@permission_required('people.change_peopleimage', (PeopleImage, 'id', 'id'))
def edit_image(request, id):
    image = get_object_or_404(PeopleImage, id=id)
    if request.method == 'POST':
        form = AddImageForm(request.POST, instance=image)
        if form.is_valid():
            people = form.cleaned_data['people']
            organisations = form.cleaned_data['organisations']
            form.save(commit=False)
            image.person_set.clear()
            image.organisation_set.clear()
            for person in people:
                image.person_set.add(Person.objects.get(id=person))
            for organisation in organisations:
                image.person_set.add(Organisation.objects.get(id=int(organisation)))
            image.save()
            return HttpResponseRedirect(reverse('view_image', args=[id]))
        else:
            people = Person.objects.filter(id__in=request.POST.getlist('people'))
            people_ids = [person.id for person in people]
            form.initial['people'] = people_ids
            organisations = Person.objects.filter(id__in=request.POST.getlist('organisations'))
            organisations_ids = [organisation.id for organisation in organisations]
            form.initial['organisations'] = organisations_ids
    else:
        people = image.person_set.all()
        people_ids = [person.id for person in people]
        organisations = image.organisation_set.all()
        organisations_ids = [organisation.id for organisation in organisations]
        if image.earliest_date:
            earliest_date = prepare_date(image.earliest_date, image.earliest_month_known, image.earliest_day_known)
        else:
            earliest_date = None
        if image.latest_date:
            latest_date = prepare_date(image.latest_date, image.latest_month_known, image.latest_day_known)
        else:
            latest_date = None
        form = AddImageForm(instance=image, initial={
            'people': people_ids,
            'organisations': organisations_ids,
            'earliest_date': earliest_date,
            'latest_date': latest_date})
    return render(request, 'people/add_image.html', {
        'form': form, 'people': people, 'organisations': organisations, 'image_id': id
    })


@permission_required('people.delete_peopleimage', (PeopleImage, 'id', 'id'))
def delete_image(request, id=None):
    if request.method == 'POST':
        form = DeleteStoryForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            PeopleImage.objects.get(id=id).delete()
            return HttpResponseRedirect(reverse('image_list'))
    else:
        image = PeopleImage.objects.get(id=id)
        form = DeleteImageForm(initial={'id': id})
    return render(request, 'people/delete_image.html', {
        'form': form, 'image': image
    })



