from django import forms
from django.forms import ModelForm
from app.people.models import *
from app.places.models import *
from app.sources.models import *
from django.forms.extras.widgets import SelectDateWidget
from calendar import monthrange
from django.conf import settings
from django.forms.models import inlineformset_factory
from django_select2 import *

from app.generic.forms import AddEventForm, DateSelectMixin, ShortDateForm
from app.places.forms import AddAddressForm


YEARS = [year for year in range(1850, 2013)]


class NewSelectDateWidget(SelectDateWidget):
    none_value = (0, 'unknown')


class PeopleMultiChoice(AutoModelSelect2MultipleField):
    queryset = Person.objects
    search_fields = ['family_name__istartswith', ]


class PersonChoice(AutoModelSelect2Field):
    queryset = Person.objects
    search_fields = ['family_name__istartswith', ]


class PlaceChoice(AutoModelSelect2Field):
    queryset = Place.objects
    search_fields = ['display_name__istartswith', 'place_name__istartswith']


class OrganisationChoice(AutoModelSelect2Field):
    queryset = Organisation.objects
    search_fields = ['display_name__istartswith', 'name__istartswith']


class LifeEventChoice(AutoModelSelect2Field):
    queryset = LifeEvent.objects


class SourcesMultiChoice(AutoModelSelect2MultipleField):
    queryset = Source.objects
    search_fields = ['title__icontains', ]


class EventLocationsMultiChoice(AutoModelSelect2MultipleField):
    queryset = EventLocation.objects
    search_fields = ['label__icontains', ]


class AddPersonForm(ModelForm, DateSelectMixin):
    # These are CharFields so they don't get vaildated as dates
    related_person = forms.ModelChoiceField(
                queryset=PersonAssociatedPerson.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
                )
    source = forms.ModelChoiceField(
                queryset=Source.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
                )
    creator_type = forms.CharField(required=False, widget=forms.HiddenInput())
    birth_earliest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=YEARS), required=False)
    birth_latest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=YEARS), required=False)
    death_earliest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=YEARS), required=False)
    death_latest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=YEARS), required=False)

    def clean(self):
        cleaned_data = super(AddPersonForm, self).clean()
        birth_earliest_date = cleaned_data['birth_earliest_date']
        birth_latest_date = cleaned_data['birth_latest_date']
        cleaned_data['birth_earliest_month_known'] = self.clean_month(birth_earliest_date, 'start')
        cleaned_data['birth_earliest_day_known'] = self.clean_day(birth_earliest_date, 'start')
        cleaned_data['birth_latest_month_known'] = self.clean_month(birth_latest_date, 'end')
        cleaned_data['birth_latest_day_known'] = self.clean_day(birth_latest_date, 'end')
        cleaned_data['birth_earliest_date'] = self.clean_date(birth_earliest_date, 'start')
        cleaned_data['birth_latest_date'] = self.clean_date(birth_latest_date, 'end')
        death_earliest_date = cleaned_data['death_earliest_date']
        death_latest_date = cleaned_data['death_latest_date']
        cleaned_data['death_earliest_month_known'] = self.clean_month(death_earliest_date, 'start')
        cleaned_data['death_earliest_day_known'] = self.clean_day(death_earliest_date, 'start')
        cleaned_data['death_latest_month_known'] = self.clean_month(death_latest_date, 'end')
        cleaned_data['death_latest_day_known'] = self.clean_day(death_latest_date, 'end')
        cleaned_data['death_earliest_date'] = self.clean_date(death_earliest_date, 'start')
        cleaned_data['death_latest_date'] = self.clean_date(death_latest_date, 'end')
        return cleaned_data

    class Meta:
        model = Person
        exclude = ('added_by', 'status')
        widgets = {
                    'birth_earliest_month_known': forms.HiddenInput,
                    'birth_earliest_day_known': forms.HiddenInput,
                    'birth_latest_month_known': forms.HiddenInput,
                    'birth_latest_day_known': forms.HiddenInput,
                    'death_earliest_month_known': forms.HiddenInput,
                    'death_earliest_day_known': forms.HiddenInput,
                    'death_latest_month_known': forms.HiddenInput,
                    'death_latest_day_known': forms.HiddenInput,
                    'biography': forms.Textarea(attrs={
                                                'class': 'input-xlarge',
                                                'rows': '4'}),
                    'mosman_connection': forms.Textarea(attrs={
                                                'class': 'input-xlarge',
                                                'rows': '4'})
                }


class UpdatePersonForm(AddPersonForm):
    pass


class ApprovePersonForm(ModelForm):

    class Meta:
        model = Person
        fields = ('status',)


class AddAltNameForm(ModelForm):
    person = PersonChoice()
    sources = SourcesMultiChoice(required=False)

    class Meta:
        model = AlternativePersonName
        exclude = ('added_by',)


class AddLifeEventForm(AddEventForm):
    person = PersonChoice()
    sources = SourcesMultiChoice(required=False)
    #event_type = forms.ModelChoiceField(queryset=LifeEventType.objects.all(), required=False)

    class Meta:
        model = LifeEvent
        exclude = ('added_by',)
        widgets = {
                    'start_earliest_month': forms.HiddenInput,
                    'start_earliest_day': forms.HiddenInput,
                    'start_latest_month': forms.HiddenInput,
                    'start_latest_day': forms.HiddenInput,
                    'end_earliest_month': forms.HiddenInput,
                    'end_earliest_day': forms.HiddenInput,
                    'end_latest_month': forms.HiddenInput,
                    'end_latest_day': forms.HiddenInput,
                    'description': forms.Textarea(attrs={
                                                'class': 'input-large',
                                                'rows': '4'})
                }


class AddEventLocationForm(forms.ModelForm):
    lifeevent = LifeEventChoice()
    location = PlaceChoice(required=False)

    class Meta:
        model = EventLocation


class AddBirthForm(AddEventForm):
    person = PersonChoice()
    location = PlaceChoice(required=False)
    sources = SourcesMultiChoice(required=False)

    class Meta:
        model = Birth
        exclude = ('added_by',)


class AddDeathForm(AddEventForm):
    person = PersonChoice()
    location = PlaceChoice(required=False)
    sources = SourcesMultiChoice(required=False)

    class Meta:
        model = Death
        exclude = ('added_by',)


class AddRankForm(ShortDateForm):
    person = forms.ModelChoiceField(
                queryset=Person.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
                )
    sources = SourcesMultiChoice(required=False)

    class Meta:
        model = Rank
        exclude = ('added_by',)


class AddServiceNumberForm(ModelForm):
    person = forms.ModelChoiceField(
                queryset=Person.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
                )
    sources = SourcesMultiChoice(required=False)

    class Meta:
        model = ServiceNumber
        exclude = ('added_by',)


class AddOrganisationForm(ModelForm):
    person = forms.ModelChoiceField(
                queryset=Person.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
        )
    associated_person = forms.ModelChoiceField(
                queryset=Person.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
        )

    class Meta:
        model = Organisation
        exclude = ('added_by',)


class AddAssociatedPersonForm(ShortDateForm):
    person = PersonChoice()
    associated_person = PersonChoice(required=False)
    sources = SourcesMultiChoice(required=False)

    class Meta:
        model = PersonAssociatedPerson
        exclude = ('added_by',)


class AddAssociatedOrganisationForm(ModelForm, DateSelectMixin):
    person = forms.ModelChoiceField(
                queryset=Person.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
        )
    start_earliest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=YEARS), required=False)
    end_earliest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=YEARS), required=False)
    organisation = OrganisationChoice()
    sources = SourcesMultiChoice(required=False)

    def clean(self):
        cleaned_data = super(AddAssociatedOrganisationForm, self).clean()
        start_earliest_date = cleaned_data['start_earliest_date']
        cleaned_data['start_earliest_month'] = self.clean_month(start_earliest_date, 'start')
        cleaned_data['start_earliest_day'] = self.clean_day(start_earliest_date, 'start')
        cleaned_data['start_earliest_date'] = self.clean_date(start_earliest_date, 'start')
        end_earliest_date = cleaned_data['end_earliest_date']
        cleaned_data['end_earliest_month'] = self.clean_month(end_earliest_date, 'start')
        cleaned_data['end_earliest_day'] = self.clean_day(end_earliest_date, 'start')
        cleaned_data['end_earliest_date'] = self.clean_date(end_earliest_date, 'start')
        return cleaned_data

    class Meta:
        model = PersonAssociatedOrganisation
        exclude = ('added_by',)
        widgets = {
                    'start_earliest_month': forms.HiddenInput,
                    'start_earliest_day': forms.HiddenInput,
                    'end_earliest_month': forms.HiddenInput,
                    'end_earliest_day': forms.HiddenInput,
                }


class AddPersonAddressForm(ModelForm, DateSelectMixin):
    person = forms.ModelChoiceField(
                queryset=Person.objects.all(),
                required=False,
                widget=forms.Select(attrs={'readonly': 'readonly'})
        )
    start_earliest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=YEARS), required=False)
    end_earliest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=YEARS), required=False)
    sources = SourcesMultiChoice(required=False)

    def clean(self):
        cleaned_data = super(AddPersonAddressForm, self).clean()
        start_earliest_date = cleaned_data['start_earliest_date']
        cleaned_data['start_earliest_month_known'] = self.clean_month(start_earliest_date, 'start')
        cleaned_data['start_earliest_day_known'] = self.clean_day(start_earliest_date, 'start')
        cleaned_data['start_earliest_date'] = self.clean_date(start_earliest_date, 'start')
        end_earliest_date = cleaned_data['end_earliest_date']
        cleaned_data['end_earliest_month_known'] = self.clean_month(end_earliest_date, 'start')
        cleaned_data['end_earliest_day_known'] = self.clean_day(end_earliest_date, 'start')
        cleaned_data['end_earliest_date'] = self.clean_date(end_earliest_date, 'start')
        return cleaned_data

    class Meta:
        model = PersonAddress
        exclude = ('added_by',)
        widgets = {
                    'start_earliest_month_known': forms.HiddenInput,
                    'start_earliest_day_known': forms.HiddenInput,
                    'start_latest_month_known': forms.HiddenInput,
                    'start_latest_day_known': forms.HiddenInput,
                    'end_earliest_month_known': forms.HiddenInput,
                    'end_earliest_day_known': forms.HiddenInput,
                    'end_latest_month_known': forms.HiddenInput,
                    'end_latest_day_known': forms.HiddenInput,
                }



class AddResourceForm(ModelForm, DateSelectMixin):
    years = [year for year in range(1850, 2013)]

    earliest_date = forms.CharField(widget=NewSelectDateWidget(attrs={'class': 'input-small'}, years=years), required=False)
    latest_date = forms.CharField(widget=NewSelectDateWidget(attrs={'class': 'input-small'}, years=years), required=False)
    earliest_month_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    earliest_day_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    latest_month_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    latest_day_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    people_choices = [(id, id) for id in Person.objects.values_list('id', flat=True)]
    people = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput, choices=people_choices, required=False)
    organisations_choices = [(id, id) for id in Organisation.objects.values_list('id', flat=True)]
    organisations = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput, choices=organisations_choices, required=False)

    def clean_earliest_date(self):
        return self.clean_date(self.cleaned_data['earliest_date'], 'start')

    def clean_latest_date(self):
        return self.clean_date(self.cleaned_data['latest_date'], 'end')

    def clean_earliest_month_known(self):
        return self.clean_month(self.cleaned_data['earliest_date'], 'start')

    def clean_earliest_day_known(self):
        return self.clean_day(self.cleaned_data['earliest_date'], 'start')

    def clean_latest_month_known(self):
        return self.clean_month(self.cleaned_data['latest_date'], 'end')

    def clean_latest_day_known(self):
        return self.clean_day(self.cleaned_data['latest_date'], 'end')


class AddStoryForm(AddResourceForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xxlarge'}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-xxlarge'}))

    class Meta:
        model = PeopleStory
        fields = ('title', 'text', 'people', 'organisations')


class DeleteStoryForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput)


class AddImageForm(AddResourceForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xxlarge'}))
    caption = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-xxlarge'}))

    class Meta:
        model = PeopleImage
        fields = ('title', 'image', 'earliest_date', 'latest_date', 'caption', 'people', 'organisations')


class DeleteImageForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput)


