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
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse, reverse_lazy

from guardian.shortcuts import assign

from rdflib import Graph
from rdflib import Namespace, BNode, Literal, RDF, URIRef

from app.linkeddata.views import LinkedDataView, LinkedDataListView, RDFSchema
from app.linkeddata.models import RDFSchema
from app.people.models import *
from app.sources.models import *
from app.places.models import *
from app.sources.forms import *

from moatools.client import MOAClient
from rstools.utilities import parse_date, convert_date_to_iso
from awmtools.client import RollClient, EmbarkationClient, RedCrossClient, HonoursClient


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


class SourceListView(LinkedDataListView):
    model = Source
    path = '/sources/{}results'
    template_name = 'sources/sources'
    browse_field = 'title'
    queryset = Source.objects.all()

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


class ImageListView(LinkedDataListView):
    model = Source
    path = '/images/results'
    template_name = 'sources/images'
    queryset = Source.objects.exclude(sourceimage=None).filter(source_type__label='photograph')

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


class StoryView(LinkedDataView):
    model = Story
    path = '/stories/%s'
    template_name = 'sources/story'

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
        graph.add((this_entity, namespaces['dc']['creator'], Literal(entity.added_by.username)))
        for person in entity.person_set.all():
            graph.add((this_entity, namespaces['foaf']['topic'], URIRef(host_ns[person.get_absolute_url()])))
        return graph


class StoryListView(LinkedDataListView):
    model = Story
    path = '/stories/results'
    template_name = 'sources/stories'
    queryset = Story.objects.all()

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
    referers = [
        'birth',
        'death',
        'lifeevent',
        'rank',
        'name',
        'servicenumber',
        'story',
        'relationship',
        'membership',
        'address'
    ]

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('sources.add_source'))
    def dispatch(self, *args, **kwargs):
        return super(AddSourceView, self).dispatch(*args, **kwargs)

    # This lets us get the user in the form
    def get_form_kwargs(self):
        kwargs = super(AddSourceView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def associate_people(self, people, association):
        for person in people:
            assoc_link, created = PersonAssociatedSource.objects.get_or_create(
                person=person,
                source=self.object,
                association=association,
                defaults={'added_by': self.request.user}
            )

    def associate_creators(self, creators, role):
        for creator in creators:
            creator_link = SourcePerson(person=creator, source=self.object, role=role)
            creator_link.save()

    def get_initial(self):
        initial = {}
        entity_type = self.kwargs.get('entity_type', None)
        entity_id = self.kwargs.get('entity_id', None)
        initial[entity_type] = entity_id
        '''
        event_type = self.kwargs.get('event_type', None)
        event_id = self.kwargs.get('event_id', None)
        initial[event_type] = event_id
        assoc_type = self.kwargs.get('assoc_type', None)
        assoc_id = self.kwargs.get('assoc_id', None)
        if assoc_type == 'people':
            initial['associated_people'] = assoc_id
        elif assoc_type == 'personorganisation':
            initial['person_organisation'] = assoc_id
        elif assoc_type == 'address':
            initial['address'] = assoc_id
        '''
        return initial

    def update_referer(self, field):
        referer = self.form.cleaned_data.get(field, None)
        if referer:
            referer.sources.add(self.object)
            referer.save()

    def form_valid(self, form):
        self.form = form
        source = form.save(commit=False)
        source.added_by = self.request.user
        category = form.cleaned_data['category']
        source_type = form.cleaned_data.get('source_type', None)
        if not source_type:
            source_type = SourceType.objects.get(label=category)
        source.source_type = source_type
        source.save()
        self.object = source
        # creators
        #author_role = SourceRole.objects.get(label='author')
        #editor_role = SourceRole.objects.get(label='editor')
        #authors = form.cleaned_data['authors']
        #editors = form.cleaned_data['editors']
        #self.associate_creators(authors, author_role)
        #self.associate_creators(editors, editor_role)
        # Subjects
        mainperson = form.cleaned_data['mainperson']
        person = form.cleaned_data['person']
        if mainperson:
            primary_topic = SourceAssociation.objects.get(label='primary topic of')
            self.associate_people([mainperson], primary_topic)
        if person:
            topic = SourceAssociation.objects.get(label='topic of')
            self.associate_people([person], topic)
        for referer in self.referers:
            self.update_referer(referer)
        '''
        associated_people = form.cleaned_data.get('associated_people', None)
        if associated_people:
            associated_people.sources.add(source)
            associated_people.save()
        person_organisation = form.cleaned_data.get('person_organisation', None)
        if person_organisation:
            person_organisation.sources.add(source)
            person_organisation.save()
        person_address = form.cleaned_data.get('address', None)
        if person_address:
            person_address.sources.add(source)
            person_address.save()
        '''
        # Permissions
        assign('sources.change_source', self.request.user, source)
        assign('sources.delete_source', self.request.user, source)
        # Extra processing
        if source.collection and source.collection.repository_item_id == 'B2455':
            self.get_moa_page(form)
        if source.collection:
            if source.collection.url == 'http://www.awm.gov.au/research/people/roll_of_honour/':
                self.process_roll_of_honour()
            elif source.collection.url == 'http://www.awm.gov.au/research/people/nominal_rolls/first_world_war_embarkation/':
                self.process_embarkation_roll()
            elif source.collection.url == 'http://www.awm.gov.au/research/people/wounded_and_missing/':
                self.process_red_cross()
            elif source.collection.url == 'http://www.awm.gov.au/research/people/honours_and_awards/':
                self.process_honours()
            elif source.collection.url == 'http://www.cwgc.org/find-war-dead.aspx':
                self.process_cwgc()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        #birth = self.form.cleaned_data.get('birth_record', None)
        #death = self.form.cleaned_data.get('death_record', None)
        #associated_people = self.form.cleaned_data.get('associated_people', None)
        url = reverse_lazy('source-update', args=[self.object.id])
        return url

    def get_naa_record(self, barcode):
        current_user = self.request.user
        system_user = User.objects.get(username='system')
        rs = RSItemClient()
        rsseries = RSSeriesClient()
        item_details = rs.get_summary(barcode)
        dates = item_details['contents_dates']
        citation = '{}, {}'.format(
            item_details['series'],
            item_details['control_symbol']
        )
        if item_details['digitised_status'] is True:
            item_url = 'http://dhistory.org/archives/naa/items/{}/'.format(barcode)
        else:
            item_url = 'http://www.naa.gov.au/cgi-bin/Search?O=I&Number={}'.format(barcode)
        series_details = rsseries.get_summary(item_details['series'])
        repository, created = Repository.objects.get_or_create(
            name='National Archives of Australia',
            defaults={'added_by': system_user}
        )
        series_type = SourceType.objects.get(label='series')
        series, created = Source.objects.get_or_create(
            repository_item_id=item_details['series'],
            source_type=series_type,
            repository=repository,
            defaults={
                'added_by': system_user,
                'title': series_details['title'],
                'url': 'http://www.naa.gov.au/cgi-bin/Search?Number={}'.format(item_details['series'])
            }

        )
        item_type = SourceType.objects.get(label='item')
        item, created = Source.objects.get_or_create(
            collection=series,
            source_type=item_type,
            collection_item_id=item_details['control_symbol'],
            repository_item_id=item_details['identifier'],
            repository=repository,
            defaults={
                'title': item_details['title'],
                'publication_date': dates['start_date']['date'],
                'publication_date_month': dates['start_date']['month'],
                'publication_date_day': dates['start_date']['day'],
                'publication_date_end': dates['end_date']['date'],
                'publication_date_end_month': dates['end_date']['month'],
                'publication_date_end_day': dates['end_date']['day'],
                'pages': item_details['digitised_pages'],
                'citation': citation,
                'url': item_url,
                'rdf_url': 'http://dhistory.org/archives/naa/items/{}/#file'.format(barcode)
            }

        )
        if created:
            assign('sources.change_source', current_user, item)
            assign('sources.delete_source', current_user, item)
        return item

    def get_moa_page(self, form):
        ''' If it's an NAA WWI service record, automatically check for a MoA page. '''
        try:
            barcode = re.search(r'Barcode=(\d+)', self.object.url).group(1)
        except AttributeError:
            barcode = re.search(r'\/(\d+)\/$', self.object.url).group(1)
        person = self.object.main_people()[0]
        moa = MOAClient()
        current_user = self.request.user
        system_user = User.objects.get(username='system')
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
                added_by=system_user
            )
            moa_page, created = Source.objects.get_or_create(
                title='Mapping Our Anzacs - {} {}'.format(
                    details['other_names'],
                    details['family_name']
                ),
                url=moa.MOA_URL.format(barcode),
                source_type=webpage_type,
                collection=moa_site,
                defaults={'added_by': current_user}
            )
            if created:
                assign('sources.change_source', current_user, moa_page)
                assign('sources.delete_source', current_user, moa_page)
            primary_topic = SourceAssociation.objects.get(label='primary topic of')
            person_source, created = PersonAssociatedSource.objects.get_or_create(
                person=person,
                source=moa_page,
                association=primary_topic,
                defaults={'added_by': current_user})
            if created:
                assign('people.change_personassociatedsource', current_user, person_source)
                assign('people.delete_personassociatedsource', current_user, person_source)
            person_name, created = AlternativePersonName.objects.get_or_create(
                person=person,
                family_name=details['family_name'],
                other_names=details['other_names'],
                defaults={'added_by': current_user}
            )
            if created:
                assign('people.change_alternativepersonname', current_user, person_name)
                assign('people.delete_alternativepersonname', current_user, person_name)
            person_name.sources.add(self.object)
            person_name.save()
            birth_place, created = Place.objects.get_or_create(
                display_name=details['place_of_birth'],
                defaults={'added_by': current_user}
            )
            if created:
                assign('places.change_place', current_user, birth_place)
                assign('places.delete_place', current_user, birth_place)
            birth = Birth.objects.create(
                label='Born at {}'.format(birth_place),
                person=person,
                location=birth_place,
                added_by=current_user
            )
            assign('people.change_birth', current_user, birth)
            assign('people.delete_birth', current_user, birth)
            birth.sources.add(self.object)
            birth.save()
            enlistment_type = LifeEventType.objects.get(label='enlistment')
            enlistment_place, created = Place.objects.get_or_create(
                display_name=details['place_of_enlistment'],
                defaults={'added_by': current_user}
            )
            if created:
                assign('places.change_place', current_user, enlistment_place)
                assign('places.delete_place', current_user, enlistment_place)
            enlistment = LifeEvent.objects.create(
                label='Enlisted at {}'.format(enlistment_place),
                type_of_event=enlistment_type,
                person=person,
                added_by=current_user
            )
            assign('people.change_lifeevent', current_user, enlistment)
            assign('people.delete_lifeevent', current_user, enlistment)
            enlistment.sources.add(self.object)
            enlistment.save()
            location_association = EventLocationAssociation.objects.get(label='happened in')
            event_location, created = EventLocation.objects.get_or_create(
                lifeevent=enlistment,
                location=enlistment_place,
                association=location_association,
                defaults={'added_by': current_user}
            )
            if created:
                assign('people.change_eventlocation', current_user, event_location)
                assign('people.delete_eventlocation', current_user, event_location)
            if details['ww2_file']['barcode']:
                item = self.get_naa_record(details['ww2_file']['barcode'])
                person_source, created = PersonAssociatedSource.objects.get_or_create(
                    person=person,
                    source=item,
                    association=primary_topic,
                    defaults={'added_by': current_user})
                if created:
                    assign('people.change_personassociatedsource', current_user, person_source)
                    assign('people.delete_personassociatedsource', current_user, person_source)
            if details['see_also']['barcode']:
                item = self.get_naa_record(details['see_also']['barcode'])
                person_source, created = PersonAssociatedSource.objects.get_or_create(
                    person=person,
                    source=item,
                    association=primary_topic,
                    defaults={'added_by': current_user})
                if created:
                    assign('people.change_personassociatedsource', current_user, person_source)
                    assign('people.delete_personassociatedsource', current_user, person_source)
            if details['also_known_as']:
                alt_name, created = AlternativePersonName.get_or_create(
                    person=person,
                    display_name=details['also_known_as'],
                    defaults={'added_by': current_user}
                )
                if created:
                    assign('people.change_alternativepersonname', current_user, alt_name)
                    assign('people.delete_alternativepersonname', current_user, alt_name)
                alt_name.sources.add(self.object)
            if details['next_of_kin']:
                try:
                    relation_name, relation = re.search(r'^(.+) \((.+)\)$', details['next_of_kin']).groups()
                except AttributeError:
                    pass
                else:
                    related_person = Person.objects.create(
                        display_name=relation_name,
                        status='non-service',
                        added_by=current_user
                    )
                    assign('people.change_person', current_user, related_person)
                    assign('people.delete_person', current_user, related_person)
                    relation_type, created = PersonAssociation.objects.get_or_create(
                        label=relation
                    )
                    related_person = PersonAssociatedPerson.objects.create(
                        person=person,
                        associated_person=related_person,
                        association=relation_type,
                        added_by=current_user
                    )
                    related_person.sources.add(self.object)
                    related_person.save()
                    assign('people.change_personassociatedperson', current_user, related_person)
                    assign('people.delete_personassociatedperson', current_user, related_person)
            return True

    def process_roll_of_honour(self):
        current_user = self.request.user
        source = self.object
        person = source.main_people()[0]
        details = self.form.cleaned_data['details']
        # NAMES
        alt_name, created = AlternativePersonName.objects.get_or_create(
            person=person,
            display_name=details['name'],
            defaults={'added_by': current_user}
        )
        if created:
            assign('people.change_alternativepersonname', current_user, alt_name)
            assign('people.delete_alternativepersonname', current_user, alt_name)
        alt_name.sources.add(self.object)
        alt_name.save()
        if details['also_known_as']:
            for alias in details['also_known_as']:
                alt_name, created = AlternativePersonName.objects.get_or_create(
                    person=person,
                    display_name=alias,
                    defaults={'added_by': current_user}
                )
                if created:
                    assign('people.change_alternativepersonname', current_user, alt_name)
                    assign('people.delete_alternativepersonname', current_user, alt_name)
                alt_name.sources.add(self.object)
                alt_name.save()
        # DEATH
        date = parse_date(details['date_of_death'])
        death_location, created = Place.objects.get_or_create(
            display_name=details['place_of_death'],
            defaults={'added_by': current_user}
        )
        if created:
            assign('places.change_place', current_user, death_location)
            assign('places.delete_place', current_user, death_location)
        burial_location, created = Place.objects.get_or_create(
            display_name=details['cemetery_or_memorial_details'],
            defaults={'added_by': current_user}
        )
        if created:
            assign('places.change_place', current_user, burial_location)
            assign('places.delete_place', current_user, burial_location)
        death = Death.objects.create(
            person=person,
            cause_of_death=details['cause_of_death'],
            start_earliest_date=date['date'],
            start_earliest_month=date['month'],
            start_earliest_day=date['day'],
            location=death_location,
            burial_place=burial_location,
            added_by=current_user
        )
        death.sources.add(source)
        assign('people.change_death', current_user, death)
        assign('people.delete_death', current_user, death)
        # DETAILS
        rank, created = Rank.objects.get_or_create(
            person=person,
            rank=details['rank'],
            added_by=current_user
        )
        rank.sources.add(source)
        if created:
            assign('people.change_rank', current_user, rank)
            assign('people.delete_rank', current_user, rank)
        service_number, created = ServiceNumber.objects.get_or_create(
            person=person,
            service_number=details['service_number'],
            added_by=current_user
        )
        service_number.sources.add(source)
        if created:
            assign('people.change_servicenumber', current_user, service_number)
            assign('people.delete_servicenumber', current_user, service_number)
        unit = '{}, {}'.format(details['unit'], details['service'])
        org, created = Organisation.objects.get_or_create(
            display_name=unit,
            defaults={'added_by': current_user}
        )
        if created:
            assign('people.change_organisation', current_user, org)
            assign('people.delete_organisation', current_user, org)
        org_association = PersonOrgAssociation.objects.get(label='member of')
        person_org = PersonAssociatedOrganisation.objects.create(
            person=person,
            organisation=org,
            association=org_association,
            added_by=current_user
        )
        assign('people.change_personassociatedorganisation', current_user, person_org)
        assign('people.delete_personassociatedorganisation', current_user, person_org)
        person_org.sources.add(source)
        return True

    def process_embarkation_roll(self):
        current_user = self.request.user
        source = self.object
        person = source.main_people()[0]
        details = self.form.cleaned_data['details']
        # Specific stuff
        # NAMES
        alt_name, created = AlternativePersonName.objects.get_or_create(
            person=person,
            display_name=details['name'],
            defaults={'added_by': current_user}
        )
        if created:
            assign('people.change_alternativepersonname', current_user, alt_name)
            assign('people.delete_alternativepersonname', current_user, alt_name)
        alt_name.sources.add(self.object)
        alt_name.save()
        # DETAILS
        rank, created = Rank.objects.get_or_create(
            person=person,
            rank=details['rank'],
            added_by=current_user
        )
        rank.sources.add(source)
        rank.save()
        if created:
            assign('people.change_rank', current_user, rank)
            assign('people.delete_rank', current_user, rank)
        service_number, created = ServiceNumber.objects.get_or_create(
            person=person,
            service_number=details['service_number'],
            added_by=current_user
        )
        service_number.sources.add(source)
        service_number.save()
        if created:
            assign('people.change_servicenumber', current_user, service_number)
            assign('people.delete_servicenumber', current_user, service_number)
        embarkation_type = LifeEventType.objects.get(label='embarkation')
        embarkation_place, created = Place.objects.get_or_create(
            display_name=details['place_of_embarkation'],
            defaults={'added_by': current_user}
        )
        if created:
                assign('places.change_place', current_user, embarkation_place)
                assign('places.delete_place', current_user, embarkation_place)
        date = parse_date(details['date_of_embarkation'])
        embarkation = LifeEvent.objects.create(
            label='Embarked from {} on the {}'.format(
                details['place_of_embarkation'],
                details['ship_embarked_on']
            ),
            person=person,
            type_of_event=embarkation_type,
            start_earliest_date=date['date'],
            start_earliest_month=date['month'],
            start_earliest_day=date['day'],
            added_by=current_user
        )
        embarkation.sources.add(source)
        embarkation.save()
        assign('people.change_lifeevent', current_user, embarkation)
        assign('people.delete_lifeevent', current_user, embarkation)
        location_association = EventLocationAssociation.objects.get(label='departed from')
        event_location = EventLocation.objects.create(
            lifeevent=embarkation,
            location=embarkation_place,
            association=location_association,
            added_by=current_user
        )
        assign('people.change_eventlocation', current_user, event_location)
        assign('people.delete_eventlocation', current_user, event_location)
        return True

    def process_red_cross(self):
        current_user = self.request.user
        source = self.object
        person = source.main_people()[0]
        details = self.form.cleaned_data['details']
        # Specific stuff
        # NAMES
        alt_name, created = AlternativePersonName.objects.get_or_create(
            person=person,
            display_name=details['name'],
            defaults={'added_by': current_user}
        )
        if created:
            assign('people.change_alternativepersonname', current_user, alt_name)
            assign('people.delete_alternativepersonname', current_user, alt_name)
        alt_name.sources.add(self.object)
        alt_name.save()
        # DETAILS
        rank, created = Rank.objects.get_or_create(
            person=person,
            rank=details['rank'],
            added_by=current_user
        )
        rank.sources.add(source)
        rank.save()
        if created:
            assign('people.change_rank', current_user, rank)
            assign('people.delete_rank', current_user, rank)
        service_number, created = ServiceNumber.objects.get_or_create(
            person=person,
            service_number=details['service_number'],
            added_by=current_user
        )
        service_number.sources.add(source)
        service_number.save()
        if created:
            assign('people.change_servicenumber', current_user, service_number)
            assign('people.delete_servicenumber', current_user, service_number)
        return True

    def process_honours(self):
        current_user = self.request.user
        source = self.object
        person = source.main_people()[0]
        details = self.form.cleaned_data['details']
        # Specific stuff
        # NAMES
        alt_name, created = AlternativePersonName.objects.get_or_create(
            person=person,
            display_name=details['name'],
            defaults={'added_by': current_user}
        )
        if created:
            assign('people.change_alternativepersonname', current_user, alt_name)
            assign('people.delete_alternativepersonname', current_user, alt_name)
        alt_name.sources.add(self.object)
        alt_name.save()
        # DETAILS
        rank, created = Rank.objects.get_or_create(
            person=person,
            rank=details['rank'],
            added_by=current_user
        )
        rank.sources.add(source)
        rank.save()
        if created:
            assign('people.change_rank', current_user, rank)
            assign('people.delete_rank', current_user, rank)
        service_number, created = ServiceNumber.objects.get_or_create(
            person=person,
            service_number=details['service_number'],
            added_by=current_user
        )
        service_number.sources.add(source)
        service_number.save()
        if created:
            assign('people.change_servicenumber', current_user, service_number)
            assign('people.delete_servicenumber', current_user, service_number)
        unit = '{}, {}'.format(details['unit'], details['service'])
        org, created = Organisation.objects.get_or_create(
            display_name=unit,
            defaults={'added_by': current_user}
        )
        if created:
            assign('people.change_organisation', current_user, org)
            assign('people.delete_organisation', current_user, org)
        org_association = PersonOrgAssociation.objects.get(label='member of')
        person_org = PersonAssociatedOrganisation.objects.create(
            person=person,
            organisation=org,
            association=org_association,
            added_by=current_user
        )
        assign('people.change_personassociatedorganisation', current_user, person_org)
        assign('people.delete_personassociatedorganisation', current_user, person_org)
        person_org.sources.add(source)
        if details['date_of_recommendation']:
            date = parse_date(details['date_of_recommendation'])
        elif details['date_of_london_gazette']:
            date = parse_date(details['date_of_london_gazette'])
        elif details['date_of_commonwealth_of_australia_gazette']:
            date = parse_date(details['date_of_commonwealth_of_australia_gazette'])
        else:
            date = None
        if details['recommendation']:
            award = 'Recommended: {}'.format(details['recommendation'])
        elif details['award']:
            award = 'Awarded: {}'.format(details['award'])
        award_type = LifeEventType.objects.get(label='award')
        awarded = LifeEvent.objects.create(
            label=award,
            person=person,
            type_of_event=award_type,
            added_by=current_user
        )
        if date:
            awarded.start_earliest_date = date['date']
            awarded.start_earliest_month = date['month']
            awarded.start_earliest_day = date['day']
        awarded.sources.add(source)
        awarded.save()
        assign('people.change_lifeevent', current_user, awarded)
        assign('people.delete_lifeevent', current_user, awarded)
        return True

    def process_cwgc(self):
        current_user = self.request.user
        source = self.object
        person = source.main_people()[0]
        details = self.form.cleaned_data['details']
        # NAMES
        alt_name, created = AlternativePersonName.objects.get_or_create(
            person=person,
            display_name=details['name'].title(),
            defaults={'added_by': current_user}
        )
        if created:
            assign('people.change_alternativepersonname', current_user, alt_name)
            assign('people.delete_alternativepersonname', current_user, alt_name)
        alt_name.sources.add(self.object)
        alt_name.save()
        # DETAILS
        if details['rank']:
            rank, created = Rank.objects.get_or_create(
                person=person,
                rank=details['rank'],
                added_by=current_user
            )
            rank.sources.add(source)
            rank.save()
            if created:
                assign('people.change_rank', current_user, rank)
                assign('people.delete_rank', current_user, rank)
        if details['service_no']:
            service_number, created = ServiceNumber.objects.get_or_create(
                person=person,
                service_number=details['service_no'],
                added_by=current_user
            )
            service_number.sources.add(source)
            service_number.save()
            if created:
                assign('people.change_servicenumber', current_user, service_number)
                assign('people.delete_servicenumber', current_user, service_number)
        if details['unit']:
            unit = '{}{}'.format(
                details['unit'],
                ', {}'.format(details['service']) if details['service'] else ''
            )
            org, created = Organisation.objects.get_or_create(
                display_name=unit,
                defaults={'added_by': current_user}
            )
            if created:
                assign('people.change_organisation', current_user, org)
                assign('people.delete_organisation', current_user, org)
            org_association = PersonOrgAssociation.objects.get(label='member of')
            person_org = PersonAssociatedOrganisation.objects.create(
                person=person,
                organisation=org,
                association=org_association,
                added_by=current_user
            )
            assign('people.change_personassociatedorganisation', current_user, person_org)
            assign('people.delete_personassociatedorganisation', current_user, person_org)
            person_org.sources.add(source)
        cemetery_source, created = Source.objects.get_or_create(
            title='Cemetery details &ndash; {}'.format(details['cemetery']['name'].title()),
            collection=source.collection,
            source_type=source.source_type,
            url=details['cemetery']['url'],
            defaults={'added_by': current_user}
        )
        if created:
            assign('sources.change_source', current_user, cemetery_source)
            assign('sources.delete_source', current_user, cemetery_source)
        burial_place, created = Place.objects.get_or_create(
            place_name=details['cemetery']['name'].title(),
            state=details['cemetery']['locality'],
            country=details['cemetery']['country'],
            defaults={'added_by': current_user}
        )
        if created:
            assign('places.change_place', current_user, burial_place)
            assign('places.delete_place', current_user, burial_place)
        burial_place.sources.add(cemetery_source)
        burial_place.save()
        if details['date_of_death']:
            date = datetime.datetime.strptime(details['date_of_death'], '%d/%m/%Y')
        else:
            date = None
        death = Death.objects.create(
            person=person,
            burial_place=burial_place,
            added_by=current_user
        )
        if date:
            death.start_earliest_date = date
            death.start_earliest_month = True
            death.start_earliest_day = True
        death.sources.add(source)
        death.save()
        assign('people.change_death', current_user, death)
        assign('people.delete_death', current_user, death)
        return True


class UpdateSourceView(PermissionRequiredMixin, UpdateView):
    template_name = 'sources/add_source.html'
    form_class = UpdateSourceForm
    model = Source
    permission_required = 'sources.change_source'

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

    def get_context_data(self, **kwargs):
        context = super(UpdateSourceView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['images'] = ImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['images'] = ImageFormSet(instance=self.object)
        context.update(kwargs)
        return context

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
                    association=association,
                    added_by=self.object.added_by)
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
        context = self.get_context_data()
        images = context['images']
        if images.is_valid() and form.is_valid():
            #organisations = form.cleaned_data['organisations']
            source = form.save(commit=False)
            source.save()
            self.object = source
            images.instance = self.object
            images.save()
            # creators
            author_role = SourceRole.objects.get(label='author')
            editor_role = SourceRole.objects.get(label='editor')
            authors = form.cleaned_data['authors']
            editors = form.cleaned_data['editors']
            self.associate_creators(authors, author_role)
            self.associate_creators(editors, editor_role)
            # subjects
            main_people = form.cleaned_data['main_people']
            other_people = form.cleaned_data['other_people']
            primary_topic = SourceAssociation.objects.get(label='primary topic of')
            topic = SourceAssociation.objects.get(label='topic of')
            self.associate_people(main_people, primary_topic)
            self.associate_people(other_people, topic)
            #for organisation in organisations:
             #   link.person_set.add(Organisation.objects.get(id=int(organisation)))
            return HttpResponseRedirect(reverse('source-view', args=[source.id]))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class DeleteSource(PermissionRequiredMixin, DeleteView):
    model = Source
    template_name = 'sources/confirm_delete.html'
    permission_required = 'source.delete_source'

    def get_success_url(self):
        return reverse_lazy('source-list')


class AddSourcePersonView(CreateView):
    template_name = 'sources/add_source_creator.html'
    form_class = AddSourcePersonForm
    model = SourcePerson

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('people.add_sourceperson'))
    def dispatch(self, *args, **kwargs):
        return super(AddSourcePersonView, self).dispatch(*args, **kwargs)

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


class AddStory(CreateView):
    model = Story
    form_class = AddStoryForm
    referers = ['person']

    # Use this instead the Guardian Permission mixin -
    # it doesn't seem to like CreateView
    @method_decorator(permission_required('source.add_story'))
    def dispatch(self, *args, **kwargs):
        return super(AddStory, self).dispatch(*args, **kwargs)

    def get_initial(self):
        entity_id = self.kwargs.get('entity_id', None)
        entity_type = self.kwargs.get('entity_type', None)
        initial = {entity_type: entity_id}
        return initial

    def update_referer(self, field):
        referer = self.form.cleaned_data.get(field, None)
        if referer:
            referer.stories.add(self.object)
            referer.save()

    def form_valid(self, form):
        self.form = form
        obj = form.save(commit=False)
        obj.added_by = self.request.user
        obj.save()
        self.object = obj
        assign('source.change_story', self.request.user, obj)
        assign('source.delete_story', self.request.user, obj)
        for referer in self.referers:
            self.update_referer(referer)
        return HttpResponseRedirect(reverse('story-update', args=[obj.id]))


class UpdateStory(PermissionRequiredMixin, UpdateView):
    model = Story
    form_class = AddStoryForm
    permission_required = 'source.change_story'

    def prepare_date(self, name):
        date = getattr(self.object, name)
        name = name[:-5]
        if date:
            year = date.year
            month = date.month
            day = date.day
            if getattr(self.object, '{}_month'.format(name)) is False:
                month = 0
            if getattr(self.object, '{}_day'.format(name)) is False:
                day = 0
            date = '{}-{}-{}'.format(year, month, day)
        return date

    def get_initial(self):
        initial = {}
        initial['start_earliest_date'] = self.prepare_date('start_earliest_date')
        initial['end_earliest_date'] = self.prepare_date('end_earliest_date')
        return initial

    def get_success_url(self):
        if 'continue' in self.request.POST:
            url = reverse_lazy('story-update', args=[self.object.id])
        else:
            url = reverse_lazy('story-view', args=[self.object.id])
        return url


class DeleteStory(PermissionRequiredMixin, DeleteView):
    model = Story
    template_name = 'sources/confirm_delete.html'
    permission_required = 'source.delete_story'

    def get_success_url(self):
        return reverse_lazy('story-list')
