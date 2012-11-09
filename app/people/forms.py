from django import forms
from django.forms import ModelForm
from app.people.models import *
from django.forms.extras.widgets import SelectDateWidget
from calendar import monthrange


class NewSelectDateWidget(SelectDateWidget):
    none_value = (0, 'unknown')


class AddResourceForm(ModelForm):
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

    def clean_date(self, date, type):
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
        return '%s-%s-%s' % (year, month, day)

    def clean_month(self, date, type):
        year, month, day = date.split('-')
        return False if int(month) == 0 else True

    def clean_day(self, date, type):
        year, month, day = date.split('-')
        return False if int(day) == 0 else True


class AddStoryForm(AddResourceForm):

    class Meta:
        model = PeopleStory
        fields = ('title', 'text', 'people', 'organisations')


class DeleteStoryForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput)


class AddImageForm(AddResourceForm):

    class Meta:
        model = PeopleImage
        fields = ('title', 'image', 'earliest_date', 'latest_date', 'caption', 'people', 'organisations')


class DeleteImageForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput)

