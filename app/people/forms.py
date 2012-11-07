from django import forms
from django.forms import ModelForm
from app.people.models import *


class AddStoryForm(ModelForm):
    people_choices = [(id, id) for id in Person.objects.values_list('id', flat=True)]
    people = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput, choices=people_choices, required=True)

    class Meta:
        model = PeopleStory
        fields = ('title', 'text')


class DeleteStoryForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput)

