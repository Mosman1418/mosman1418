# Create your views here.

# Create your views here.
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from app.linkeddata.views import LinkedDataView
from app.linkeddata.models import RDFSchema
from app.sources.models import *


class SourceView(LinkedDataView):
    model = Source
    path = '/sources/%s'
    template_name = 'sources/source'

    def make_graph(self, entity):
        namespaces = {}
        graph = Graph()
        schemas = RDFSchema.objects.all()
        for schema in schemas:
            namespace = Namespace(schema.uri)
            graph.bind(schema.prefix, namespace)
            namespaces[schema.prefix] = namespace
        person_ns = Namespace('http://mosman1418/sources/')
        person = URIRef(person_ns[str(entity.id)])
        graph.add((person, namespaces['rdfs']['label'], Literal(str(entity))))
        return graph
