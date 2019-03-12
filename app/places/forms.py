from django import forms
from django.forms import ModelForm
from app.people.models import *
from app.places.models import *
from app.sources.models import *
from django.forms.widgets import SelectDateWidget
from calendar import monthrange
from django.conf import settings

from django_select2.forms import (
    ModelSelect2Widget, Select2Widget
)
from app.people.models import *
from app.places.models import *


class BirthChoice(ModelSelect2Widget):
    queryset = Birth.objects


class DeathChoice(ModelSelect2Widget):
    queryset = Death.objects


class EventChoice(ModelSelect2Widget):
    queryset = EventLocation.objects


class PlaceChoice(ModelSelect2Widget):
    queryset = Place.objects
    search_fields = ['display_name__istartswith', 'place_name__istartswith']


class AddPlaceForm(ModelForm):
    birth_event = BirthChoice(required=False)
    death_event = DeathChoice(required=False)
    life_event = EventChoice(required=False)

    class Meta:
        model = Place
        exclude = ('added_by', )


class AddAddressForm(ModelForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    person_address = forms.ModelChoiceField(
        queryset=PersonAddress.objects.all(),
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    place = PlaceChoice(required=False)

    class Meta:
        model = Address
        exclude = ('added_by', )
        widgets = {
            'mosman_street': Select2Widget()
        }


class PlaceMergeForm(forms.Form):
    merge_record = forms.ModelChoiceField(
        queryset=Place.objects.all(),
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    master_record = PlaceChoice()
