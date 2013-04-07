# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.sites.models import Site
from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from app.linkeddata.views import LinkedDataView, LinkedDataListView, RDFSchema
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


class MemorialPhotosView(LinkedDataView):
    model = Memorial
    path = '/memorials/%s/photos'
    template_name = 'memorials/memorial_photos'

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


class MemorialListView(LinkedDataListView):
    model = Memorial
    path = '/memorials/{}results'
    template_name = 'memorials/memorials'

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

