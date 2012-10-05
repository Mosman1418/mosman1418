# Create your views here.
import httplib
import itertools
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.cache import patch_vary_headers
from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef
from django_conneg.views import ContentNegotiatedView
from django_conneg.decorators import renderer

from app.linkeddata.models import *

SCHEMAS = {
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'foaf': 'http://xmlns.com/foaf/0.1/',
            'dc': 'http://purl.org/dc/terms/',
            'bio': 'http://purl.org/vocab/bio/0.1/',
            'geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#',
            'rel': 'http://purl.org/vocab/relationship/',
            'graves': 'http://rdf.muninn-project.org/ontologies/graves#'
            }


class LinkedDataView(ContentNegotiatedView):
    model = None
    path = ''
    template_name = ''

    def get(self, request, id=None, format=None):
        context = {}
        if format:
            context['entity'] = self.model.objects.get(id=id)
            return self.render_to_format(request, context, self.template_name, format)
        else:
            context['status_code'] = 303
            context['additional_headers'] = {'location': self.path % id}
            context['entity'] = None
            return self.render(request, context, self.template_name)

    def render(self, request, context, template_name):
        """
        Returns a HttpResponse of the right media type as specified by the
        request.
        context can contain status_code and additional_headers members, to set
        the HTTP status code and headers of the request, respectively.
        template_name should lack a file-type suffix (e.g. '.html', as
        renderers will append this as necessary.
        """
        status_code = context.pop('status_code', httplib.OK)
        additional_headers = context.pop('additional_headers', {})

        self.set_renderers(request)

        for renderer in request.renderers:
            response = renderer(self, request, context, template_name)
            if response is NotImplemented:
                continue
            response.status_code = status_code
            response.renderer = renderer
            break
        else:
            tried_mimetypes = list(itertools.chain(*[r.mimetypes for r in request.renderers]))
            response = self.http_not_acceptable(request, tried_mimetypes)
            response.renderer = None
        for key, value in additional_headers.iteritems():
            # My changes -- Modify location for 303 redirect
            if key == 'location' and response.renderer:
                response[key] = '%s.%s/' % (value, response.renderer.format)
            else:
                response[key] = value
            # End my changes

        # We're doing content-negotiation, so tell the user-agent that the
        # response will vary depending on the accept header.
        patch_vary_headers(response, ('Accept',))
        return response

    @renderer(format='html', mimetypes=('text/html', 'application/xhtml+xml'), name='HTML', priority=1)
    def render_html(self, request, context, template_name):
        if context['entity']:
            template_name = self.join_template_name(template_name, 'html')
            return render_to_response(template_name, context, context_instance=RequestContext(request), mimetype='text/html')
        else:
            return HttpResponse(content='')

    @renderer(format='json', mimetypes=('application/json',), name='JSON')
    def render_json(self, request, context, template_name):
        if context['entity']:
            #data = {'name': context['memorial'].name}
            graph = self.make_graph(context['entity'])
            return HttpResponse(graph.serialize(format='json-ld', indent=4), mimetype='application/json')
        else:
            return HttpResponse(content='')

    @renderer(format='rdf', mimetypes=('application/rdf+xml',), name='RDF')
    def render_rdf(self, request, context, template_name):
        if context['entity']:
            graph = self.make_graph(context['entity'])
            return HttpResponse(graph.serialize(format='pretty-xml'), mimetype='application/rdf+xml')
        else:
            return HttpResponse(content='')

    @renderer(format='ttl', mimetypes=('text/turtle',), name='TURTLE')
    def render_ttl(self, request, context, template_name):
        if context['entity']:
            graph = self.make_graph(context['entity'])
            return HttpResponse(graph.serialize(format='turtle'), mimetype='text/turtle')
        else:
            return HttpResponse(content='')


