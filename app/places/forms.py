from django import forms
from django.forms import ModelForm
from app.people.models import *
from app.places.models import *
from app.sources.models import *
from django.forms.extras.widgets import SelectDateWidget
from calendar import monthrange
from django.conf import settings
from django_select2 import *

from app.people.models import *
from app.places.models import *


class BirthChoice(AutoModelSelect2Field):
    queryset = Birth.objects


class DeathChoice(AutoModelSelect2Field):
    queryset = Death.objects


class EventChoice(AutoModelSelect2Field):
    queryset = EventLocation.objects


class AddPlaceForm(ModelForm):
    birth_event = BirthChoice(required=False)
    death_event = DeathChoice(required=False)
    life_event = EventChoice(required=False)

    class Meta:
        model = Place
        exclude = ('added_by', )

