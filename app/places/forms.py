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


class AddPlaceForm(ModelForm):
    birth_record = BirthChoice(required=False)
    death_record = DeathChoice(required=False)

    class Meta:
        model = Place
        exclude = ('added_by', )

