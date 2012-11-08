from django import forms
from django.forms import ModelForm
from app.people.models import *


class AddResourceForm(ModelForm):
    people_choices = [(id, id) for id in Person.objects.values_list('id', flat=True)]
    people = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput, choices=people_choices, required=False)
    organisations_choices = [(id, id) for id in Organisation.objects.values_list('id', flat=True)]
    organisations = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput, choices=organisations_choices, required=False)


class AddStoryForm(AddResourceForm):

    class Meta:
        model = PeopleStory
        fields = ('title', 'text', 'people', 'organisations')


class DeleteStoryForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput)


class AddImageForm(AddResourceForm):

    class Meta:
        model = PeopleImage
        fields = ('title', 'image', 'caption', 'people', 'organisations')


class DeleteImageForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput)

