# -*- coding: utf-8 -*-

import re
import datetime
from urllib.request import urlopen, URLError, HTTPError
import json
from bs4 import BeautifulSoup

from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django_select2.forms import (
    ModelSelect2Widget, Select2Widget, ModelSelect2MultipleWidget)
from ckeditor.widgets import CKEditorWidget 

from app.sources.models import *
from app.people.models import *
from app.generic.forms import DateSelectMixin, ShortDateForm

from django.forms.widgets import SelectDateWidget
from calendar import monthrange

from rstools.client import RSItemClient, RSSeriesClient
from moatools.client import MOAClient
from awmtools.client import RollClient, EmbarkationClient, RedCrossClient, HonoursClient, CollectionClient
from cwgctools.client import CWGCClient

TROVE_API_KEY = 'ierj9cpsh7f5u7kg'

def get_range_upper_year():
    now = datetime.datetime.now().year
    return now + 1

YEARS = [year for year in range(1850, get_range_upper_year())]


class NewSelectDateWidget(SelectDateWidget):
    none_value = (0, 'unknown')


class PeopleMultiChoices(ModelSelect2MultipleWidget):
    queryset = Person.objects
    search_fields = ['family_name__istartswith', ]


class SourceChoice(ModelSelect2Widget):
    queryset = Source.objects


class CollectionChoice(ModelSelect2Widget):
    queryset = Source.objects
    search_fields = ['title__icontains']


class RepositoryChoice(ModelSelect2Widget):
    queryset = Repository.objects
    search_fields = ['display_name__icontains']


class AuthorMultiChoices(ModelSelect2MultipleWidget):
    queryset = Person.objects
    search_fields = ['family_name__istartswith', ]


class SourcesMultiChoice(ModelSelect2MultipleWidget):
    queryset = Source.objects
    search_fields = ['title__icontains', ]


class SourceImageForm(ModelForm):
    class Meta:
        model = SourceImage
        exclude = ('added_by',)
        widgets = {
            'page': forms.TextInput(attrs={'class': 'input-mini'})
        }


ImageFormSet = inlineformset_factory(Source, SourceImage, form=SourceImageForm, extra=1)


class AddSourceForm(ModelForm, DateSelectMixin):
    categories = (
        ('website', 'website'),
        ('webpage', 'webpage'),
        ('letter', 'letter'),
        ('diary', 'diary'),
        ('photograph', 'photograph'),
        ('trove', 'Trove newspaper article'),
        ('naa', 'National Archives of Australia file or document'),
        ('awm', 'Australian War Memorial database record'),
        ('cwgc', 'Commonwealth War Graves Commission database record')
    )
    publication_date = forms.CharField(widget=NewSelectDateWidget(
        attrs={'class': 'input-small'},
        years=YEARS), required=False)
    print(publication_date)
    publication_date_end = forms.CharField(widget=NewSelectDateWidget(
        attrs={'class': 'input-small'},
        years=YEARS), required=False)
    main_people = PeopleMultiChoices(required=False)
    other_people = PeopleMultiChoices(required=False)
    category = forms.ChoiceField(choices=categories)
    collection = CollectionChoice(required=False)
    repository = RepositoryChoice(required=False)
    authors = AuthorMultiChoices(required=False)
    editors = AuthorMultiChoices(required=False)
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    mainperson = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    organisation = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    birth = forms.ModelChoiceField(
        queryset=Birth.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    death = forms.ModelChoiceField(
        queryset=Death.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    lifeevent = forms.ModelChoiceField(
        queryset=LifeEvent.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    name = forms.ModelChoiceField(
        queryset=AlternativePersonName.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    rank = forms.ModelChoiceField(
        queryset=Rank.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    servicenumber = forms.ModelChoiceField(
        queryset=ServiceNumber.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    relationship = forms.ModelChoiceField(
        queryset=PersonAssociatedPerson.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'}))
    address = forms.ModelChoiceField(
        queryset=PersonAddress.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'}))
    membership = forms.ModelChoiceField(
        queryset=PersonAssociatedOrganisation.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'}))
    story = forms.ModelChoiceField(
        queryset=Story.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )

    def __init__(self, user, *args, **kwargs):
        super(AddSourceForm, self).__init__(*args, **kwargs)
        self.user = user

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
            if category == 'trove' or category == 'naa' or category == 'awm' or category == 'cwgc':
                if 'url' not in cleaned_data:
                    self._errors['url'] = self.error_class(['A url is required'])
                else:
                    if category == 'trove':
                        cleaned_data = self.get_trove_newspaper(cleaned_data)
                    elif category == 'naa':
                        cleaned_data = self.get_naa_record(cleaned_data)
                    elif category == 'awm':
                        cleaned_data = self.get_awm_record(cleaned_data)
                    elif category == 'cwgc':
                        cleaned_data = self.get_cwgc_record(cleaned_data)
        return cleaned_data

    def get_trove_newspaper(self, cleaned_data):
        patterns = [
            re.compile(r'http://trove.nla.gov.au/ndp/del/article/(\d+)'),
            re.compile(r'http://nla.gov.au/nla.news-article(\d+)')
        ]
        url = cleaned_data['url']
        print (url)
        id = None
        for pattern in patterns:
            try:
                id = pattern.search(url).group(1)
                break
            except AttributeError:
                continue
        if not id:
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
        cleaned_data['publication_date_month_known'] = True
        cleaned_data['publication_date_day_known'] = True
        cleaned_data['pages'] = data['article']['page']
        cleaned_data['url'] = data['article']['troveUrl']
        cleaned_data['source_type'] = source_type
        if 'title' in self._errors:
            del self._errors['title']
        if 'source_type' in self._errors:
            del self._errors['source_type']
        return cleaned_data

    def get_naa_record(self, cleaned_data):
        current_user = self.user
        system_user = User.objects.get(username='system')
        url = cleaned_data['url']
        try:
            if 'dhistory' in url:
                barcode = re.search(r'naa\/items\/(\d+)', url).group(1)
            else:
                barcode = re.search(r'Barcode=(\d+)', url).group(1)
        except AttributeError:
            self._errors['url'] = self.error_class(['Not a valid NAA url'])
            return cleaned_data
        rs = RSItemClient()
        rsseries = RSSeriesClient()
        item_details = rs.get_summary(barcode)
        print (item_details)
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
        cleaned_data['rdf_url'] = 'http://dhistory.org/archives/naa/items/{}/#file'.format(barcode)
        if 'title' in self._errors:
            del self._errors['title']
        if 'source_type' in self._errors:
            del self._errors['source_type']
        return cleaned_data

    def get_awm_record(self, cleaned_data):
        system_user = User.objects.get(username='system')
        url = cleaned_data['url']
        publisher = 'Australian War Memorial'
        website_type = SourceType.objects.get(label='website')
        webpage_type = SourceType.objects.get(label='webpage')
        if 'roll_of_honour' in url:
            collection, created = Source.objects.get_or_create(
                title='Roll of Honour',
                publisher=publisher,
                source_type=website_type,
                url='http://www.awm.gov.au/research/people/roll_of_honour/',
                defaults={'added_by': system_user}
            )
            awm = RollClient()
        elif 'embarkation' in url:
            collection, created = Source.objects.get_or_create(
                title='First World War Embarkation Roll',
                publisher=publisher,
                source_type=website_type,
                url='http://www.awm.gov.au/research/people/nominal_rolls/first_world_war_embarkation/',
                defaults={'added_by': system_user}
            )
            awm = EmbarkationClient()
        elif 'wounded_and_missing' in url:
            collection, created = Source.objects.get_or_create(
                title='First World War Red Cross Wounded and Missing',
                publisher=publisher,
                source_type=website_type,
                url='http://www.awm.gov.au/research/people/wounded_and_missing/',
                defaults={'added_by': system_user}
            )
            awm = RedCrossClient()
        elif 'honours_and_awards' in url:
            collection, created = Source.objects.get_or_create(
                title='Honours and Awards',
                publisher=publisher,
                source_type=website_type,
                url='http://www.awm.gov.au/research/people/honours_and_awards/',
                defaults={'added_by': system_user}
            )
            awm = HonoursClient()
        details = awm.get_details(url=url)
        cleaned_data['details'] = details
        cleaned_data['title'] = details['title']
        cleaned_data['source_type'] = webpage_type
        cleaned_data['collection'] = collection
        cleaned_data['url'] = url
        if 'title' in self._errors:
            del self._errors['title']
        if 'source_type' in self._errors:
            del self._errors['source_type']
        return cleaned_data

    def get_cwgc_record(self, cleaned_data):
        system_user = User.objects.get(username='system')
        url = cleaned_data['url']
        publisher = 'Commonwealth War Graves Commission'
        website_type = SourceType.objects.get(label='website')
        webpage_type = SourceType.objects.get(label='webpage')
        cwgc = CWGCClient()
        url = cleaned_data['url']
        details = cwgc.get_details(url)
        collection, created = Source.objects.get_or_create(
            title='Find War Dead',
            publisher=publisher,
            source_type=website_type,
            url='http://www.cwgc.org/find-war-dead.aspx',
            defaults={'added_by': system_user}
        )
        cleaned_data['details'] = details
        cleaned_data['title'] = 'Find War Dead &ndash; {}'.format(details['name'].title())
        cleaned_data['source_type'] = webpage_type
        cleaned_data['collection'] = collection
        cleaned_data['url'] = url
        if 'title' in self._errors:
            del self._errors['title']
        if 'source_type' in self._errors:
            del self._errors['source_type']
        return cleaned_data

    class Meta:
        model = Source
        exclude = ('added_by',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-xxlarge'}),
            'url': forms.TextInput(attrs={'class': 'input-xxlarge'}),
            'caption': CKEditorWidget(attrs={'class': 'input-xlarge'}),
        }


class UpdateSourceForm(ModelForm, DateSelectMixin):
    publication_date = forms.CharField(widget=NewSelectDateWidget(
        attrs={'class': 'input-small'},
        years=YEARS), required=False)
    publication_date_end = forms.CharField(widget=NewSelectDateWidget(
        attrs={'class': 'input-small'},
        years=YEARS), required=False)
    main_people = PeopleMultiChoices(required=False)
    other_people = PeopleMultiChoices(required=False)
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
        exclude = ('added_by',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-xlarge'}),
            'url': forms.TextInput(attrs={'class': 'input-xlarge'}),
            'caption': CKEditorWidget(attrs={'class': 'input-xlarge'}),
        }


class AddSourcePersonForm(ModelForm):
    family_name = forms.CharField()
    other_names = forms.CharField(required=False)

    class Meta:
        model = SourcePerson
        exclude = ('person', 'added_by',)
        widgets = {
            'source': forms.Select(attrs={'readonly': True})
        }


class AddStoryForm(ShortDateForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.filter(status='confirmed'),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'}))
    sources = SourcesMultiChoice(required=False)

    class Meta:
        model = Story
        exclude = ('added_by',)
        widgets = {
            'text': CKEditorWidget(attrs={'class': 'input-xlarge'}),
            'credit': CKEditorWidget(attrs={'class': 'input-xlarge'}),
        }
