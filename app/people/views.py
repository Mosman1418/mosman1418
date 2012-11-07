# Create your views here.
from django.shortcuts import render_to_response, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sites.models import Site
import json
from django.http import HttpResponse, HttpResponseRedirect
from guardian.decorators import permission_required
from django.core.urlresolvers import reverse

from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from guardian.shortcuts import assign

from app.linkeddata.views import LinkedDataView, RDFSchema
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


class PeopleStoryView(LinkedDataView):
    model = PeopleStory
    path = '/people/story/%s'
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
def add_story(request, id=None):
    person = None
    if request.method == 'POST':
        form = AddStoryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            people = form.cleaned_data['people']
            story = PeopleStory.objects.create(title=title, text=text, created_by=request.user)
            for person in people:
                story.person_set.add(Person.objects.get(id=int(person)))
            story.save()
            assign('people.change_peoplestory', request.user, story)
            assign('people.delete_peoplestory', request.user, story)
            return HttpResponseRedirect(reverse('people_edit_story', args=[story.id]))
    else:
        if id:
            person = Person.objects.get(id=id)
        form = AddStoryForm()
    return render(request, 'people/add_story.html', {
        'form': form, 'people': [person], 'story_id': None
    })


@permission_required('people.change_peoplestory', (PeopleStory, 'id', 'id'))
def edit_story(request, id):
    story = get_object_or_404(PeopleStory, id=id)
    if request.method == 'POST':
        form = AddStoryForm(request.POST or None, instance=story)
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            people = form.cleaned_data['people']
            story.title = title
            story.text = text
            story.person_set.all().delete()
            for person in people:
                story.person_set.add(Person.objects.get(id=int(person)))
            story.save()
            return HttpResponseRedirect(reverse('people_edit_story', args=[id]))
    else:
        people = story.person_set.all()
        form = AddStoryForm(instance=story)
    return render(request, 'people/add_story.html', {
        'form': form, 'people': people, 'story_id': id
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

