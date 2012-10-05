# Create your views here.
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from app.linkeddata.views import LinkedDataView, SCHEMAS
from app.people.models import *


class PersonView(LinkedDataView):
    model = Person
    path = '/people/%s'
    template_name = 'people/person'

    def make_graph(self, entity):
        prefixes = ['rdfs', 'foaf', 'owl']
        schemas = {prefix: Namespace(SCHEMAS[prefix]) for prefix in prefixes}
        graph = Graph()
        for prefix, namespace in schemas.items():
            graph.bind(prefix, namespace)
        person_ns = Namespace('http://mosman1418/people/')
        person = URIRef(person_ns[str(entity.id)])
        graph.add((person, schemas['rdfs']['label'], Literal(str(entity))))
        graph.add((person, schemas['foaf']['name'], Literal(str(entity))))
        graph.add((person, schemas['foaf']['familyName'], Literal(entity.family_name)))
        if entity.other_names:
            graph.add((person, schemas['foaf']['givenName'], Literal(entity.other_names)))
        return graph


def show_person(request, id):
    person = People.objects.get(id=id)
    return render(request, 'people/person.html', {'person': person})


def show_people(request):
    results = People.objects.all().order_by('family_name', 'other_names')
    paginator = Paginator(results, 25)
    page = request.GET.get('page')
    try:
        people = paginator.page(page)
    except PageNotAnInteger:
        people = paginator.page(1)
    except EmptyPage:
        people = paginator.page(paginator.num_pages)
    return render(request, 'people/people.html', {'people': people})
