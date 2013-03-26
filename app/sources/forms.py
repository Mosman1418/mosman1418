import re
import datetime
from urllib2 import urlopen, URLError, HTTPError
import json
from bs4 import BeautifulSoup

from django import forms
from django.forms import ModelForm
from django_select2 import *

from app.sources.models import *
from app.people.models import *

from django.forms.extras.widgets import SelectDateWidget
from calendar import monthrange

from rstools.client import RSItemClient, RSSeriesClient
from moatools.client import MOAClient
from awmtools.client import RollClient, EmbarkationClient, RedCrossClient, HonoursClient, CollectionClient


TROVE_API_KEY = 'ierj9cpsh7f5u7kg'

YEARS = [year for year in range(1850, 2013)]


class NewSelectDateWidget(SelectDateWidget):
    none_value = (0, 'unknown')


class DateSelectMixin(object):
    def clean_date(self, date, type):
        if date:
            year, month, day = date.split('-')
            if int(month) == 0:
                if type == 'start':
                    month = '1'
                    day = '1'
                elif type == 'end':
                    month = '12'
                    day = '31'
            else:
                if int(day) == 0:
                    if type == 'start':
                        day = '1'
                    elif type == 'end':
                        day = monthrange(int(year), int(month))[1]
            date = '%s-%s-%s' % (year, month, day)
        else:
            date = None
        return date

    def clean_month(self, date, type):
        if date:
            year, month, day = date.split('-')
            status = False if int(month) == 0 else True
        else:
            status = False
        return status

    def clean_day(self, date, type):
        if date:
            year, month, day = date.split('-')
            status = False if int(day) == 0 else True
        else:
            status = False
        return status


class PeopleMultiChoices2(AutoSelect2MultipleField):

    def get_val_txt(self, value):
        person = Person.objects.get(id=value)
        return '{}, {}'.format(person.family_name, person.other_names)

    def get_results(self, request, term, page, context):
        people = Person.objects.values_list('id', 'family_name', 'other_names').filter(family_name__istartswith=term).order_by('family_name')
        results = [(id, '%s, %s' % (family_name, other_names)) for id, family_name, other_names in people]
        return (NO_ERR_RESP, False, results)


class PeopleMultiChoices(AutoModelSelect2MultipleField):
    queryset = Person.objects
    search_fields = ['family_name__istartswith', ]


class SourceChoice(AutoModelSelect2Field):
    queryset = Source.objects


class CollectionChoice(AutoModelSelect2Field):
    queryset = Source.objects
    search_fields = ['title__icontains']


class RepositoryChoice(AutoModelSelect2Field):
    queryset = Repository.objects
    search_fields = ['display_name__icontains']


class AuthorMultiChoices(AutoModelSelect2MultipleField):
    queryset = Person.objects
    search_fields = ['family_name__istartswith', ]


class AddSourceForm(ModelForm, DateSelectMixin):
    categories = (
            ('website', 'website'),
            ('webpage', 'webpage'),
            ('trove', 'Trove newspaper article'),
            ('naa', 'National Archives of Australia file or document'),
            ('awm', 'Australian War Memorial database record'),
            ('cwgc', 'Commonwealth War Graves Commission database record')
        )
    main_people = PeopleMultiChoices(required=False)
    related_people = PeopleMultiChoices(required=False)
    category = forms.ChoiceField(choices=categories)
    collection = CollectionChoice(required=False)
    repository = RepositoryChoice(required=False)
    authors = AuthorMultiChoices(required=False)
    editors = AuthorMultiChoices(required=False)
    birth_record = forms.ModelChoiceField(
                queryset=Birth.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
        )
    death_record = forms.ModelChoiceField(
                queryset=Death.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
        )
    associated_people = forms.ModelChoiceField(
                queryset=PersonAssociatedPerson.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'}))

    def clean(self):
        cleaned_data = super(AddSourceForm, self).clean()
        publication_date = cleaned_data['publication_date']
        publication_date_end = cleaned_data['publication_date_end']
        cleaned_data['publication_date_month_known'] = self.clean_month(publication_date, 'start')
        cleaned_data['publication_date_day_known'] = self.clean_day(publication_date, 'start')
        cleaned_data['publication_date_end_month_known'] = self.clean_month(publication_date_end, 'end')
        cleaned_data['publication_date_end_day_known'] = self.clean_day(publication_date_end, 'end')
        cleaned_data['publication_date'] = self.clean_date(publication_date, 'start')
        cleaned_data['publication_date_end'] = self.clean_date(publication_date_end, 'end')
        if 'category' in cleaned_data:
            category = cleaned_data['category']
            if category == 'trove' or category == 'naa' or category == 'awm':
                if 'url' not in cleaned_data:
                    self._errors['url'] = self.error_class(['A url is required'])
                else:
                    if category == 'trove':
                        cleaned_data = self.get_trove_newspaper(cleaned_data)
                    elif category == 'naa':
                        cleaned_data = self.get_naa_record(cleaned_data)
                    elif category == 'awm':
                        cleaned_data = self.get_awm_record(cleaned_data)
        return cleaned_data

    def get_trove_newspaper(self, cleaned_data):
        patterns = [
            re.compile(r'http://trove.nla.gov.au/ndp/del/article/(\d+)'),
            re.compile(r'http://nla.gov.au/nla.news-article(\d+)')
        ]
        url = cleaned_data['url']
        print url
        for pattern in patterns:
            try:
                id = pattern.search(url).group(1)
                break
            except AttributeError:
                self._errors['url'] = self.error_class(['Not a valid Trove url'])
                return cleaned_data
        trove_url = 'http://api.trove.nla.gov.au/newspaper/%s?key=%s&encoding=json' % (id, TROVE_API_KEY)
        response = urlopen(trove_url)
        data = json.load(response)
        source_type = SourceType.objects.get(label='newspaper article')
        cleaned_data['title'] = data['article']['heading']
        cleaned_data['collection_title'] = data['article']['title']['value']
        date = datetime.datetime(*map(int, re.split('[^\d]', data['article']['date'])))
        cleaned_data['publication_date'] = date
        cleaned_data['publication_date_month'] = True
        cleaned_data['publication_date_day'] = True
        cleaned_data['pages'] = data['article']['page']
        cleaned_data['url'] = data['article']['troveUrl']
        cleaned_data['source_type'] = source_type
        if 'title' in self._errors:
            del self._errors['title']
        if 'source_type' in self._errors:
            del self._errors['source_type']
        return cleaned_data

    def get_naa_record(self, cleaned_data):
        url = cleaned_data['url']
        try:
            barcode = re.search(r'Barcode=(\d+)', url).group(1)
        except AttributeError:
            self._errors['url'] = self.error_class(['Not a valid NAA url'])
            return cleaned_data
        rs = RSItemClient()
        rsseries = RSSeriesClient()
        item_details = rs.get_summary(barcode)
        dates = item_details['contents_dates']
        citation = '{}, {}'.format(
                                item_details['series'],
                                item_details['control_symbol']
                            )
        if item_details['digitised_status'] == True:
            item_url = 'http://dhistory.org/archives/naa/{}/'.format(item_details['identifier'])
        series_details = rsseries.get_summary(item_details['series'])
        repository = Organisation.objects.get(name='National Archives of Australia')
        series_type = SourceType.objects.get(label='series')
        series, created = Source.objects.get_or_create(
                repository_item_id=item_details['series'],
                source_type=series_type,
                repository=repository,
                defaults={
                    'title': series_details['title']
                }

            )
        item_type = SourceType.objects.get(label='item')

        cleaned_data['collection'] = series
        cleaned_data['source_type'] = item_type
        cleaned_data['collection_item_id'] = item_details['control_symbol']
        cleaned_data['repository_item_id'] = item_details['identifier']
        cleaned_data['title'] = item_details['title']
        cleaned_data['publication_date'] = dates['start_date']['date']
        cleaned_data['publication_date_month'] = dates['start_date']['month']
        cleaned_data['publication_date_day'] = dates['start_date']['day']
        cleaned_data['publication_date_end'] = dates['end_date']['date']
        cleaned_data['publication_date_end_month'] = dates['end_date']['month']
        cleaned_data['publication_date_end_day'] = dates['end_date']['day']
        cleaned_data['pages'] = item_details['digitised_pages']
        cleaned_data['citation'] = citation
        cleaned_data['repository'] = repository
        cleaned_data['url'] = item_url
        if 'title' in self._errors:
            del self._errors['title']
        if 'source_type' in self._errors:
            del self._errors['source_type']
        return cleaned_data

    def get_awm_record(self, cleaned_data):
        url = cleaned_data['url']
        if 'roll_of_honour' in url:
            collection = Source.objects.get(title='Roll of Honour')
            details = self.process_roll_of_honour(url)
        elif 'embarkation' in url:
            collection = Source.objects.get(title='First World War Embarkation Roll')
            details = self.process_embarkation_roll
        elif 'wounded_and_missing' in url:
            collection = Source.objects.get(title='First World War Red Cross Wounded and Missing')
            details = self.process_red_cross(url)
        elif 'honours_and_awards' in url:
            collection = Source.objects.get(title='Honours and Awards')
            details = self.process_honours(url)
        webpage_type = SourceType.objects.get(label='webpage')
        cleaned_data['title'] = details['title']
        cleaned_data['source_type'] = webpage_type
        cleaned_data['collection'] = collection
        cleaned_data['url'] = url
        if 'title' in self._errors:
            del self._errors['title']
        if 'source_type' in self._errors:
            del self._errors['source_type']
        return cleaned_data

    def process_roll_of_honour(self, url):
        awm = RollClient()
        details = awm.get_details(url=url)
        # Specific stuff
        return details

    def process_embarkation_roll(self, url):
        awm = EmbarkationClient()
        details = awm.get_details(url=url)
        # Specific stuff

        return details

    def process_red_cross(self, url):
        awm = RedCrossClient()
        details = awm.get_details(url=url)
        # Specific stuff

        return details

    def process_honours(self, url):
        awm = HonoursClient()
        details = awm.get_details(url=url)
        # Specific stuff

        return details

    class Meta:
        model = Source
        exclude = ('added_by', 'source_type', 'citation', 'rdf_url', 'json_url')
        widgets = {
                    'title': forms.TextInput(attrs={'class': 'input-xxlarge'}),
                    'publication_date': NewSelectDateWidget(attrs={'class': 'input-small'}, years=YEARS),
                    'publication_date_month_known': forms.HiddenInput,
                    'publication_date_day_known': forms.HiddenInput,
                    'publication_date_end_month_known': forms.HiddenInput,
                    'publication_date_end_day_known': forms.HiddenInput,
                    'publication_date_end': NewSelectDateWidget(attrs={'class': 'input-small'}, years=YEARS),
                    'url': forms.TextInput(attrs={'class': 'input-xxlarge'}),
                }


class UpdateSourceForm(ModelForm, DateSelectMixin):

    main_people = PeopleMultiChoices(required=False)
    related_people = PeopleMultiChoices(required=False)
    collection = CollectionChoice(required=False)
    repository = RepositoryChoice(required=False)
    authors = AuthorMultiChoices(required=False)
    editors = AuthorMultiChoices(required=False)

    def clean(self):
        cleaned_data = super(UpdateSourceForm, self).clean()
        publication_date = cleaned_data['publication_date']
        publication_date_end = cleaned_data['publication_date_end']
        cleaned_data['publication_date_month_known'] = self.clean_month(publication_date, 'start')
        cleaned_data['publication_date_day_known'] = self.clean_day(publication_date, 'start')
        cleaned_data['publication_date_end_month_known'] = self.clean_month(publication_date_end, 'end')
        cleaned_data['publication_date_end_day_known'] = self.clean_day(publication_date_end, 'end')
        cleaned_data['publication_date'] = self.clean_date(publication_date, 'start')
        cleaned_data['publication_date_end'] = self.clean_date(publication_date_end, 'end')
        return cleaned_data

    class Meta:
        model = Source
        exclude = ('added_by', 'source_type', 'citation', 'rdf_url', 'json_url')
        widgets = {
                    'title': forms.TextInput(attrs={'class': 'input-xxlarge'}),
                    'publication_date': NewSelectDateWidget(attrs={'class': 'input-small'}, years=YEARS),
                    'publication_date_month_known': forms.HiddenInput,
                    'publication_date_day_known': forms.HiddenInput,
                    'publication_date_end_month_known': forms.HiddenInput,
                    'publication_date_end_day_known': forms.HiddenInput,
                    'publication_date_end': NewSelectDateWidget(attrs={'class': 'input-small'}, years=YEARS),
                    'url': forms.TextInput(attrs={'class': 'input-xxlarge'}),
                }



class AddSourcePersonForm(ModelForm):
    family_name = forms.CharField()
    other_names = forms.CharField(required=False)

    class Meta:
        model = SourcePerson
        exclude = ('person', 'added_by')
        widgets = {
                    'source': forms.Select(attrs={'readonly': True})
                }
