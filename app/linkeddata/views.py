# Create your views here.
import httplib
import itertools
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.cache import patch_vary_headers
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
        # Check for merged records and redirect if necessary
        instance = self.model.objects.get(id=id)
        try:
            redirect_to = instance.merged_into
        except AttributeError:
            pass
        else:
            if redirect_to:
                return redirect(self.model.objects.get(id=redirect_to.id), permanent=True)
        # End redirect check
        context = {}
        if format:
            context['content'] = self.model.objects.select_related().get(id=id)
            return self.render_to_format(request, context, self.template_name, format)
        else:
            context['status_code'] = 303
            context['additional_headers'] = {'location': self.path % id}
            context['content'] = None
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
        request, context, template_name = self.get_render_params(request, context, template_name)
        self.set_renderers()

        status_code = context.pop('status_code', httplib.OK)
        additional_headers = context.pop('additional_headers', {})

        for renderer in request.renderers:
            response = renderer(request, context, template_name)
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
                location = '%s.%s/' % (value, response.renderer.format)
                try:
                    #location += '?page=%s' % context['page']
                    location += '?{}'.format(context['queries'])
                except KeyError:
                    pass
                response[key] = location
            else:
                response[key] = value
            # End my changes

        # We're doing content-negotiation, so tell the user-agent that the
        # response will vary depending on the accept header.
        patch_vary_headers(response, ('Accept',))
        return response

    @renderer(format='html', mimetypes=('text/html', 'application/xhtml+xml'), name='HTML', priority=1)
    def render_html(self, request, context, template_name):
        if context['content']:
            template_name = self.join_template_name(template_name, 'html')
            identifier = 'http://%s%s' % (Site.objects.get_current().domain, context['content'].get_absolute_url())
            context['identifier'] = identifier
            context['id_path'] = identifier[:-1]
            return render_to_response(template_name, context, context_instance=RequestContext(request), mimetype='text/html')
        else:
            return HttpResponse(content='')

    @renderer(format='json', mimetypes=('application/json',), name='JSON')
    def render_json(self, request, context, template_name):
        if context['content']:
            #data = {'name': context['memorial'].name}
            graph = self.make_graph(context['content'])
            return HttpResponse(graph.serialize(format='json-ld', indent=4), mimetype='application/json')
        else:
            return HttpResponse(content='')

    @renderer(format='rdf', mimetypes=('application/rdf+xml',), name='RDF')
    def render_rdf(self, request, context, template_name):
        if context['content']:
            graph = self.make_graph(context['content'])
            return HttpResponse(graph.serialize(format='pretty-xml'), mimetype='application/rdf+xml')
        else:
            return HttpResponse(content='')

    @renderer(format='ttl', mimetypes=('text/turtle',), name='TURTLE')
    def render_ttl(self, request, context, template_name):
        if context['content']:
            graph = self.make_graph(context['content'])
            return HttpResponse(graph.serialize(format='turtle'), mimetype='text/turtle')
        else:
            return HttpResponse(content='')


class LinkedDataListView(LinkedDataView):
    browse_field = None
    queryset = None

    def get(self, request, letter=None, format=None):
        context = {}
        queries_without_page = request.GET.copy()
        if 'page' in queries_without_page:
            del queries_without_page['page']
        context['queries'] = queries_without_page
        self.path = self.path.format('{}/'.format(letter) if letter else '')
        if format:
            if self.queryset:
                results = self.queryset
                if letter and self.browse_field:
                    filter = '{}__istartswith'.format(self.browse_field)
                    results = results.filter(**{filter: letter})
            else:
                if letter and self.browse_field:
                    filter = '{}__istartswith'.format(self.browse_field)
                    results = self.model.objects.select_related().filter(**{filter: letter})
                else:
                    results = self.model.objects.select_related().all()
            if self.browse_field:
                results = results.order_by(self.browse_field)
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

    @renderer(format='html', mimetypes=('text/html', 'application/xhtml+xml'), name='HTML', priority=1)
    def render_html(self, request, context, template_name):
        if context['content'] is not None:
            template_name = self.join_template_name(template_name, 'html')
            identifier = 'http://%s%s/' % (Site.objects.get_current().domain, self.path)
            context['identifier'] = identifier
            context['id_path'] = identifier[:-1]
            return render_to_response(template_name, context, context_instance=RequestContext(request), mimetype='text/html')
        else:
            return HttpResponse(content='')


