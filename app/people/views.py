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
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
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
from app.sources.models import Source
from app.memorials.models import *


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


class PersonPhotosView(LinkedDataView):
    model = Person
    path = '/people/%s/photos'
    template_name = 'people/person_photos'

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
    path = '/people/{}results'
    template_name = 'people/people'
    browse_field = 'family_name'
    queryset = Person.objects.filter(status='confirmed').filter(merged_into__isnull=True)

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
    browse_field = 'name'
    queryset = Organisation.objects.filter(merged_into__isnull=True)

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


class PersonAddressView(LinkedDataView):
    model = PersonAddress
    path = '/people/addresses/%s'
    template_name = 'people/personaddress'

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


class PersonMembershipView(LinkedDataView):
    model = PersonAssociatedOrganisation
    path = '/people/memberships/%s'
    template_name = 'people/membership'

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
    template_name = 'people/confirm_delete.html'
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


class PersonMergeView(FormView):
    template_name = 'people/person_merge_form.html'
    form_class = PersonMergeForm

    def get_initial(self):
        id = self.kwargs.get('id', None)
        initial = {'merge_record': id}
        return initial

    def form_valid(self, form):
        merge_record = form.cleaned_data['merge_record']
        master_record = form.cleaned_data['master_record']
        # Find all properties of merged record and update
        for address in PersonAddress.objects.filter(person=merge_record):
            address.person = master_record
            address.save()
        for relation in PersonAssociatedPerson.objects.filter(person=merge_record):
            relation.person = master_record
            relation.save()
        for relation in PersonAssociatedPerson.objects.filter(associated_person=merge_record):
            relation.associated_person = master_record
            relation.save()
        for organisation in PersonAssociatedOrganisation.objects.filter(person=merge_record):
            organisation.person = master_record
            organisation.save()
        for source in PersonAssociatedSource.objects.filter(person=merge_record):
            source.person = master_record
            source.save()
        for place in PersonAssociatedPlace.objects.filter(person=merge_record):
            place.person = master_record
            place.save()
        for event in PersonAssociatedEvent.objects.filter(person=merge_record):
            event.person = master_record
            event.save()
        for obj in PersonAssociatedObject.objects.filter(person=merge_record):
            obj.person = master_record
            obj.save()
        for story in merge_record.stories.all():
            master_record.stories.add(story)
            master_record.save()
        merge_record.stories.clear()
        for rank in Rank.objects.filter(person=merge_record):
            rank.person = master_record
            rank.save()
        for num in ServiceNumber.objects.filter(person=merge_record):
            num.person = master_record
            num.save()
        for name in AlternativePersonName.objects.filter(person=merge_record):
            name.person = master_record
            name.save()
        for lifeevent in LifeEvent.objects.filter(person=merge_record):
            lifeevent.person = master_record
            lifeevent.save()
        for birth in Birth.objects.filter(person=merge_record):
            birth.person = master_record
            birth.save()
        for death in Death.objects.filter(person=merge_record):
            death.person = master_record
            death.save()
        for mem_name in MemorialName.objects.filter(person=merge_record):
            mem_name.person = master_record
            mem_name.save()
        for creator in SourcePerson.objects.filter(person=merge_record):
            creator.person = master_record
            creator.save()
        for memorial in MemorialAssociatedPerson.objects.filter(person=merge_record):
            memorial.organisation = master_record
            memorial.save()
        merge_record.merged_into = master_record
        merge_record.save()
        self.redirect = master_record
        return super(PersonMergeView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('person-view', args=[self.redirect.id])


class OrganisationMergeView(FormView):
    template_name = 'people/organisation_merge_form.html'
    form_class = OrganisationMergeForm

    def get_initial(self):
        id = self.kwargs.get('id', None)
        initial = {'merge_record': id}
        return initial

    def form_valid(self, form):
        merge_record = form.cleaned_data['merge_record']
        master_record = form.cleaned_data['master_record']
        # Find all properties of merged record and update
        for source in OrganisationAssociatedSource.objects.filter(organisation=merge_record):
            source.organisation = master_record
            source.save()
        for person in PersonAssociatedOrganisation.objects.filter(organisation=merge_record):
            person.organisation = master_record
            person.save()
        for memorial in MemorialAssociatedOrganisation.objects.filter(organisation=merge_record):
            memorial.organisation = master_record
            memorial.save()
        for story in merge_record.stories.all():
            master_record.stories.add(story)
            master_record.save()
        merge_record.stories.clear()
        merge_record.merged_into = master_record
        merge_record.save()
        self.redirect = master_record
        return super(OrganisationMergeView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('organisation-view', args=[self.redirect.id])
