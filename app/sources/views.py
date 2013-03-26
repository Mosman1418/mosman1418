# Create your views here.

# Create your views here.
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sites.models import Site
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from guardian.decorators import permission_required
from django.core.urlresolvers import reverse, reverse_lazy

from guardian.shortcuts import assign

from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from app.linkeddata.views import LinkedDataView
from app.linkeddata.models import RDFSchema
from app.people.models import *
from app.sources.models import *
from app.places.models import *
from app.sources.forms import *

from moatools.client import MOAClient


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
        host_ns = Namespace('http://%s' % (Site.objects.get_current().domain))
        this_entity = URIRef(host_ns[entity.get_absolute_url()])
        graph.add((this_entity, namespaces['rdfs']['label'], Literal(str(entity))))
        graph.add((this_entity, namespaces['dc']['title'], Literal(str(entity))))
        if entity.source_type.id == 3:
            graph.add((this_entity, namespaces['rdf']['type'], namespaces['bibo']['Article']))
            graph.add((this_entity, namespaces['dc']['isPartOf'], Literal(entity.collection_title)))
        for person in entity.person_set.all():
            graph.add((this_entity, namespaces['foaf']['topic'], URIRef(host_ns[person.get_absolute_url()])))
        return graph


def show_sources(request):
    results = Source.objects.all().order_by('title')
    paginator = Paginator(results, 25)
    page = request.GET.get('page')
    try:
        sources = paginator.page(page)
    except PageNotAnInteger:
        sources = paginator.page(1)
    except EmptyPage:
        sources = paginator.page(paginator.num_pages)
    return render(request, 'sources/sources.html', {'sources': sources})


def get_trove_newspaper(url):
    details = {}
    patterns = [
        re.compile(r'http://trove.nla.gov.au/ndp/del/article/(\d+)'),
        re.compile(r'http://nla.gov.au/nla.news-article(\d+)')
    ]
    for pattern in patterns:
        try:
            id = pattern.search(url).group(1)
            break
        except AttributeError:
            raise
    trove_url = 'http://api.trove.nla.gov.au/newspaper/%s?key=%s&encoding=json' % (id, TROVE_API_KEY)
    response = get_url(trove_url)
    data = json.load(response)
    details['title'] = data['article']['heading']
    details['newspaper'] = data['article']['title']['value']
    details['newspaper_id'] = data['article']['title']['id']
    details['date'] = data['article']['date']
    details['page'] = data['article']['page']
    details['url'] = data['article']['troveUrl']
    return details


def get_url(url):
    '''
    Retrieve page.
    '''
    response = urlopen(url)
    return response


def add_trove_newspaper(source, url):
    details = get_trove_newspaper(url)
    source.title = details['title']
    source.collection_title = details['newspaper']
    source.pages = details['page']
    source.publication_date = details['date']
    source.publication_date_month = True
    source.publication_date_day = True
    source.url = details['url']
    source.save()


class AddSourceView(CreateView):
    template_name = 'sources/add_source.html'
    form_class = AddSourceForm
    model = Source

    def associate_people(self, people, association):
        for person in people:
            assoc_link = PersonAssociatedSource(person=person,
                source=self.object, association=association)
            assoc_link.save()

    def associate_creators(self, creators, role):
        for creator in creators:
            creator_link = SourcePerson(person=creator, source=self.object, role=role)
            creator_link.save()

    def form_valid(self, form):
        self.form = form
        source = form.save(commit=False)
        source.added_by = self.request.user
        category = form.cleaned_data['category']
        if category in ['webpage', 'website']:
            source_type = SourceType.objects.get(label=category)
            source.source_type = source_type
        else:
            source.source_type = form.cleaned_data['source_type']
        source.save()
        self.object = source
        # creators
        author_role = SourceRole.objects.get(label='author')
        editor_role = SourceRole.objects.get(label='editor')
        authors = form.cleaned_data['authors']
        editors = form.cleaned_data['editors']
        self.associate_creators(authors, author_role)
        self.associate_creators(editors, editor_role)
        # Subjects
        main_people = form.cleaned_data['main_people']
        related_people = form.cleaned_data['related_people']
        #organisations = form.cleaned_data['organisations']
        primary_topic = PersonAssociation.objects.get(label='primary topic of')
        topic = PersonAssociation.objects.get(label='topic of')
        self.associate_people(main_people, primary_topic)
        self.associate_people(related_people, topic)
        #for organisation in organisations:
         #   link.person_set.add(Organisation.objects.get(id=int(organisation)))
        birth = form.cleaned_data.get('birth_record', None)
        if birth:
            print birth
            birth.sources.add(source)
            birth.save()
        death = form.cleaned_data.get('death_record', None)
        if death:
            death.sources.add(source)
            death.save()
        associated_people = form.cleaned_data.get('associated_people', None)
        if associated_people:
            associated_people.sources.add(source)
            associated_people.save()
        # Permissions
        assign('sources.change_source', self.request.user, source)
        assign('sources.delete_source', self.request.user, source)
        # Extra processing
        if source.collection and source.collection.repository_item_id == 'B2455':
            self.get_moa_page(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        birth = self.form.cleaned_data.get('birth_record', None)
        death = self.form.cleaned_data.get('death_record', None)
        associated_people = self.form.cleaned_data.get('associated_people', None)
        if birth:
            url = reverse_lazy('birth-update', args=[birth.id])
        elif death:
            url = reverse_lazy('death-update', args=[death.id])
        elif associated_people:
            url = reverse_lazy('persontoperson-update', args=[associated_people.id])
        else:
            url = reverse_lazy('source-update', args=[self.object.id])
        return url

    def get_moa_page(self, form):
        ''' If it's an NAA WWI service record, automatically check for a MoA page. '''
        try:
            barcode = re.search(r'Barcode=(\d+)', self.object.url).group(1)
        except AttributeError:
            barcode = re.search(r'\/(\d+)\/$', self.object.url).group(1)
        person = self.object.main_people()[0]
        moa = MOAClient()
        user = User.objects.get(username='system')
        try:
            details = moa.get_details(barcode)
        except (URLError, HTTPError):
            # Don't want to throw an error if the MoA server is down.
            # Should perhaps log this in some way so it can be followed up.
            pass
        else:
            website_type = SourceType.objects.get(label='website')
            webpage_type = SourceType.objects.get(label='webpage')
            moa_site, created = Source.objects.get_or_create(
                                    title='Mapping Our Anzacs',
                                    url='http://mappingouranzacs.naa.gov.au',
                                    publisher='National Archives of Australia',
                                    source_type=website_type,
                                    added_by=user)
            moa_page, created = Source.objects.get_or_create(
                                    title='{} {}'.format(
                                                        details['other_names'],
                                                        details['family_name']
                                                        ),
                                    url=moa.MOA_URL.format(barcode),
                                    source_type=webpage_type,
                                    collection=moa_site,
                                    added_by=user
                                    )
            primary_topic = PersonAssociation.objects.get(label='primary topic of')
            PersonAssociatedSource.objects.create(person=person,
                source=moa_page, association=primary_topic)
            person_name, created = AlternativePersonName.objects.get_or_create(
                                        person=person,
                                        family_name=details['family_name'],
                                        other_names=details['other_names']
                                    )
            person_name.source.add(self.object)
            person_name.save()
            birth_place, created = Place.objects.get_or_create(
                                display_name=details['place_of_birth'],
                                added_by=user
                                )
            birth, created = Birth.objects.get_or_create(
                            label='Born at {}'.format(birth_place),
                            person=person,
                            location=birth_place,
                            added_by=user,
                        )
            birth.sources.add(self.object)
            birth.save()
            enlistment_type = LifeEventType.objects.get(label='enlistment')
            enlistment_place, created = Place.objects.get_or_create(
                                display_name=details['place_of_enlistment'],
                                added_by=user
                                )
            enlistment, created = LifeEvent.objects.get_or_create(
                            label='Enlisted at {}'.format(enlistment_place),
                            event_type=enlistment_type,
                            person=person,
                            location=enlistment_place,
                            added_by=user
                        )
            enlistment.sources.add(self.object)
            enlistment.save()

            if details['ww2_file']['barcode']:
                self.get_naa_record(details['ww2_file']['barcode'])
            if details['see_also']['barcode']:
                self.get_naa_record(details['see_also']['barcode'])
            if details['also_known_as']:
                alt_name, created = AlternativePersonName.get_or_create(
                        person=person,
                        display_name=details['also_known_as'],
                    )
                alt_name.source.add(self.object)
            if details['next_of_kin']:
                try:
                    relation_name, relation = re.search(r'^(.+) \((.+)\)$', details['next_of_kin']).groups()
                except AttributeError:
                    pass
                else:
                    related_person = Person.objects.create(
                        display_name=relation_name,
                        mosman_related=False,
                        added_by=user
                        )
                    relation_type, created = PersonAssociation.objects.get_or_create(label=relation)
                    PersonAssociatedPerson.objects.create(
                        person=person,
                        associated_person=related_person,
                        association=relation_type
                        )
            return True

    def get_initial(self):
        initial = {}
        entity_type = self.kwargs.get('entity_type', None)
        entity_id = self.kwargs.get('entity_id', None)
        if entity_type == 'person':
            initial['main_people'] = [entity_id]
        elif entity_type == 'organisation':
            initial['main_organisations'] = [entity_id]
        event_type = self.kwargs.get('event_type', None)
        event_id = self.kwargs.get('event_id', None)
        if event_type == 'births':
            initial['birth_record'] = event_id
        elif event_type == 'deaths':
            initial['death_record'] = event_id
        assoc_type = self.kwargs.get('assoc_type', None)
        assoc_id = self.kwargs.get('assoc_id', None)
        if assoc_type == 'people':
            initial['associated_people'] = assoc_id
        return initial


class UpdateSourceView(UpdateView):
    template_name = 'sources/add_source.html'
    form_class = UpdateSourceForm
    model = Source

    def prepare_date(self, name):
        date = getattr(self.object, name)
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
        initial['publication_date'] = self.prepare_date('publication_date')
        initial['publication_date_end'] = self.prepare_date('publication_date_end')
        initial['authors'] = self.object.authors()
        initial['editors'] = self.object.editors()
        initial['main_people'] = self.object.main_people()
        initial['other_people'] = self.object.other_people()
        return initial

    def associate_people(self, people, association):
        # Add new
        for person in people:
            if not PersonAssociatedSource.objects.filter(
                                                person=person,
                                                source=self.object,
                                                association=association).exists():
                PersonAssociatedSource.objects.create(
                                                person=person,
                                                source=self.object,
                                                association=association)
        # Delete the deleted
        links = PersonAssociatedSource.objects.filter(
                                                source=self.object,
                                                association=association)
        for current in links:
            if current.person not in people:
                current.delete()

    def associate_creators(self, creators, role):
        for creator in creators:
            if not SourcePerson.objects.filter(person=creator, source=self.object, role=role).exists():
                SourcePerson.objects.create(person=creator, source=self.object, role=role)

        # Delete the deleted
        links = SourcePerson.objects.filter(
                                        source=self.object,
                                        role=role)
        for current in links:
            if current.person not in creators:
                current.delete()

    def form_valid(self, form):
        main_people = form.cleaned_data['main_people']
        related_people = form.cleaned_data['related_people']
        #organisations = form.cleaned_data['organisations']
        source = form.save(commit=False)
        source.save()
        self.object = source
        # creators
        author_role = SourceRole.objects.get(label='author')
        editor_role = SourceRole.objects.get(label='editor')
        authors = form.cleaned_data['authors']
        editors = form.cleaned_data['editors']
        self.associate_creators(authors, author_role)
        self.associate_creators(editors, editor_role)
        # subjects
        primary_topic = PersonAssociation.objects.get(label='primary topic of')
        topic = PersonAssociation.objects.get(label='topic of')
        self.associate_people(main_people, primary_topic)
        self.associate_people(related_people, topic)
        #for organisation in organisations:
         #   link.person_set.add(Organisation.objects.get(id=int(organisation)))
        return HttpResponseRedirect(reverse('source-view', args=[source.id]))


class AddSourcePersonView(CreateView):
    template_name = 'sources/add_source_creator.html'
    form_class = AddSourcePersonForm
    model = SourcePerson

    def get_initial(self):
        initial = {}
        source_id = self.kwargs.get('source_id', None)
        if source_id:
            initial['source'] = source_id
        return initial

    def form_valid(self, form):
        creator = form.save(commit=False)
        family_name = form.cleaned_data['family_name']
        other_names = form.cleaned_data['other_names']
        person = Person.objects.create(
                                    family_name=family_name,
                                    other_names=other_names,
                                    mosman_related=False,
                                    added_by=self.request.user
                                )
        creator.person = person
        creator.added_by = self.request.user
        creator.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        source_id = self.kwargs.get('source_id', None)
        return reverse_lazy('source-update', args=[source_id])

