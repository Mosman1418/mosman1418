# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.sites.models import Site
from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from app.linkeddata.views import LinkedDataView, RDFSchema
from app.memorials.models import *


class MemorialView(LinkedDataView):
    model = Memorial
    path = '/memorials/%s'
    template_name = 'memorials/memorial'

    def make_graph(self, memorial):
        namespaces = {}
        graph = Graph()
        schemas = RDFSchema.objects.all()
        for schema in schemas:
            namespace = Namespace(schema.uri)
            graph.bind(schema.prefix, namespace)
            namespaces[schema.prefix] = namespace
        host_ns = Namespace('http://%s' % (Site.objects.get_current().domain))
        this_memorial = URIRef(host_ns[memorial.get_absolute_url()])
        graph.add((this_memorial, namespaces['graves']['monument_title'], Literal(memorial.name)))
        for memorial_name in MemorialName.objects.filter(memorial=memorial):
            graph.add((this_memorial, namespaces['graves']['monument_name'], Literal(memorial_name.name)))
            graph.add((this_memorial, namespaces['graves']['commemorates'], URIRef(host_ns[memorial_name.person.get_absolute_url()])))
        for source in memorial.memorialassociatedsource_set.all():
            for rdf in source.association.rdf_property.all():
                graph.add((this_memorial, namespaces[rdf.schema.prefix][rdf.rdf_property], URIRef(host_ns[source.source.get_absolute_url()])))
        return graph


def show_memorial(request, id):
    memorial = Memorial.objects.get(id=id)
    return render(request, 'memorials/memorial.html', {'memorial': memorial})


def show_memorials(request):
    memorials = Memorial.objects.all().order_by('name')
    return render(request, 'memorials/memorials.html', {'memorials': memorials})


def show_memorial_rdf(request, id):
    schemas = {}
    schemas['graves'] = Namespace('http://rdf.muninn-project.org/ontologies/graves#')
    memorial = Memorial.objects.get(id=id)
    graph = ConjunctiveGraph()
    for prefix, namespace in schemas.items():
        graph.bind(prefix, namespace)
    memorials_ns = Namespace('http://mosman1418/memorials/')
    this_memorial = URIRef(memorials_ns[str(memorial.id)])
    graph.add((this_memorial, schemas['graves']['monument_title'], Literal(memorial.name)))
    for memorial_name in MemorialName.objects.filter(memorial=memorial):
        graph.add((this_memorial, schemas['graves']['monument_name'], Literal(memorial_name.name)))
    return HttpResponse(
        graph.serialize(format='pretty-xml'),
        content_type='application/xml'
    )


def create_series_rdf(request, series_id):
    series = Series.objects.get(id=series_id)
    graph = ConjunctiveGraph()
    IA_SERIES = Namespace('http://invisibleaustralians.org/series/')
    NS = add_namespaces(graph, 'Series')
    this_series = URIRef(IA_SERIES[str(series.id)])
    add_rdf_attribute(graph, NS, this_series, series, 'Series', 'name', 'literal')
    add_rdf_attribute(graph, NS, this_series, series, 'Series', 'series_number', 'literal')
    add_rdf_attribute(graph, NS, this_series, series, 'Series', 'information_link', 'uri')
    response = HttpResponse(
        graph.serialize(format='pretty-xml'),
        content_type='application/rdf+xml'
    )
    return response


def add_namespaces(graph, class_name):
    schemas = Schema.objects.filter(attribute__mapping__class_name=class_name).distinct()
    NS = {}
    for schema in schemas:
        NS[schema.prefix.upper()] = Namespace(schema.address)
        graph.bind(schema.prefix, NS[schema.prefix.upper()])
    return NS


def add_rdf_attribute(graph, NS, rdf_subject, class_object, class_name, field_name, field_type):
    attrs = Attribute.objects.filter(mapping__class_name=class_name, mapping__field_name=field_name)
    if field_type == 'literal':
        rdf_object = Literal(getattr(class_object, field_name))
    elif field_type == 'uri':
        rdf_object = URIRef(getattr(class_object, field_name))
    for attr in attrs:
        graph.add((rdf_subject, NS[attr.schema.prefix.upper()][attr.name], rdf_object))
