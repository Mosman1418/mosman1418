# Create your views here.
from django.shortcuts import render_to_response, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sites.models import Site
import json
from django.http import HttpResponse, HttpResponseRedirect
from guardian.decorators import permission_required
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from guardian.shortcuts import assign

from app.linkeddata.views import LinkedDataView, LinkedDataListView, RDFSchema
from app.people.models import *
from app.people.forms import *


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



def show_person(request, id):
    person = People.objects.get(id=id)
    return render(request, 'people/person.html', {'person': person})


def show_people(request):
    results = Person.objects.all().order_by('family_name', 'other_names')
    paginator = Paginator(results, 25)
    page = request.GET.get('page')
    try:
        people = paginator.page(page)
    except PageNotAnInteger:
        people = paginator.page(1)
    except EmptyPage:
        people = paginator.page(paginator.num_pages)
    return render(request, 'people/people.html', {'people': people})


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
        form = AddStoryForm(instance=story, initial={'people': people_ids})
        organisations = story.organisation_set.all()
        organisations_ids = [organisation.id for organisation in organisations]
        form = AddStoryForm(instance=story, initial={'people': people_ids, 'organisations': organisations_ids})
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
        people = story.person_set.all()
        people_ids = [person.id for person in people]
        form = AddStoryForm(instance=story, initial={'people': people_ids})
        organisations = story.organisation_set.all()
        organisations_ids = [organisation.id for organisation in organisations]
        form = AddStoryForm(instance=story, initial={'people': people_ids, 'organisations': organisations_ids})
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


def person_autocomplete(request):
    query = request.GET.get('query', 'a')
    num_results = request.GET.get('num_results', 10)
    page = request.GET.get('page', 1)
    num_results = request.GET.get('num_results', 10)
    start = (int(page) - 1) * int(num_results)
    end = start + int(num_results)
    options = {}
    people = Person.objects.values_list('id', 'family_name', 'other_names').filter(family_name__istartswith=query).order_by('family_name')[start:end]
    if len(people) < int(num_results):
        options['more'] = False
    else:
        options['more'] = True
    options['results'] = [{'id': id, 'text': '%s, %s' % (family_name, other_names)} for id, family_name, other_names in people]
    return HttpResponse(json.dumps(options), content_type="application/json")

