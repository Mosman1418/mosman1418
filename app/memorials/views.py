# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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


class MemorialNamesView(LinkedDataListView):
    model = MemorialName
    path = '/memorials/{}/names{}/results'
    template_name = 'memorials/memorial_names'

    def get(self, request, memorial_id, letter=None, format=None):
        context = {}
        queries_without_page = request.GET.copy()
        if 'page' in queries_without_page:
            del queries_without_page['page']
        if 'order_by' in queries_without_page:
            del queries_without_page['order_by']
        context['queries'] = queries_without_page
        context['memorial'] = Memorial.objects.get(id=memorial_id)
        self.path = self.path.format(memorial_id,
                                     '{}/'.format(letter) if letter else '')
        if format:
            order_by = request.GET.get('order_by', 'position')
            results = self.model.objects.select_related().filter(memorial=memorial_id)
            if order_by == 'family_name':
                results = results.order_by('person__family_name')
            count = request.GET.get('count', '25')
            paginator = Paginator(results, count)
            page = request.GET.get('page', '1')
            try:
                content = paginator.page(page)
            except PageNotAnInteger:
                content = paginator.page(1)
            except EmptyPage:
                content = paginator.page(paginator.num_pages)
            context['content'] = content
            context['letter'] = letter
            return self.render_to_format(request, context, self.template_name, format)
        else:
            context['queries'] = request.GET.urlencode()
            context['status_code'] = 303
            context['additional_headers'] = {'location': self.path}
            context['content'] = None
            return self.render(request, context, self.template_name)

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
        return graph


class MemorialPartNamesView(LinkedDataListView):
    model = MemorialName
    path = '/memorials/parts/{}/results'
    template_name = 'memorials/memorial_part'

    def get(self, request, part_id, letter=None, format=None):
        context = {}
        queries_without_page = request.GET.copy()
        if 'page' in queries_without_page:
            del queries_without_page['page']
        if 'order_by' in queries_without_page:
            del queries_without_page['order_by']
        context['queries'] = queries_without_page
        context['part'] = MemorialPart.objects.get(id=part_id)
        self.path = self.path.format(part_id)
        if format:
            order_by = request.GET.get('order_by', 'position')
            results = self.model.objects.select_related().filter(memorial_part=part_id)
            if order_by == 'family_name':
                results = results.order_by('person__family_name')
            count = request.GET.get('count', '25')
            paginator = Paginator(results, count)
            page = request.GET.get('page', '1')
            try:
                content = paginator.page(page)
            except PageNotAnInteger:
                content = paginator.page(1)
            except EmptyPage:
                content = paginator.page(paginator.num_pages)
            context['content'] = content
            context['letter'] = letter
            return self.render_to_format(request, context, self.template_name, format)
        else:
            context['queries'] = request.GET.urlencode()
            context['status_code'] = 303
            context['additional_headers'] = {'location': self.path}
            context['content'] = None
            return self.render(request, context, self.template_name)

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
        return graph


class MemorialListView(LinkedDataListView):
    model = Memorial
    path = '/memorials/results'
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

