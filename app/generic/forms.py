from django import forms
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from calendar import monthrange

YEARS = [year for year in range(1850, 2013)]


class NewSelectDateWidget(SelectDateWidget):
    none_value = (0, 'unknown')


class AddPersonForm(ModelForm):
    years = [year for year in range(1850, 1950)]

    birth_earliest_date = forms.CharField(widget=NewSelectDateWidget(attrs={'class': 'input-small'}, years=years), required=False)
    birth_latest_date = forms.CharField(widget=NewSelectDateWidget(attrs={'class': 'input-small'}, years=years), required=False)
    birth_earliest_month_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    birth_earliest_day_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    birth_latest_month_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    birth_latest_day_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    death_earliest_date = forms.CharField(widget=NewSelectDateWidget(attrs={'class': 'input-small'}, years=years), required=False)
    death_latest_date = forms.CharField(widget=NewSelectDateWidget(attrs={'class': 'input-small'}, years=years), required=False)
    death_earliest_month_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    death_earliest_day_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    death_latest_month_known = forms.BooleanField(widget=forms.HiddenInput, required=False)
    death_latest_day_known = forms.BooleanField(widget=forms.HiddenInput, required=False)

    def clean_birth_earliest_date(self):
        return self.clean_date(self.cleaned_data['birth_earliest_date'], 'start')

    def clean_death_earliest_date(self):
        return self.clean_date(self.cleaned_data['death_earliest_date'], 'start')

    def clean_birth_latest_date(self):
        return self.clean_date(self.cleaned_data['birth_latest_date'], 'end')

    def clean_death_latest_date(self):
        return self.clean_date(self.cleaned_data['death_latest_date'], 'end')

    def clean_birth_earliest_month_known(self):
        return self.clean_month(self.cleaned_data['birth_earliest_date'], 'start')

    def clean_death_earliest_month_known(self):
        return self.clean_month(self.cleaned_data['death_earliest_date'], 'start')

    def clean_birth_earliest_day_known(self):
        return self.clean_day(self.cleaned_data['birth_earliest_date'], 'start')

    def clean_death_earliest_day_known(self):
        return self.clean_day(self.cleaned_data['death_earliest_date'], 'start')

    def clean_birth_latest_month_known(self):
        return self.clean_month(self.cleaned_data['birth_latest_date'], 'end')

    def clean_death_latest_month_known(self):
        return self.clean_month(self.cleaned_data['death_latest_date'], 'end')

    def clean_birth_latest_day_known(self):
        return self.clean_day(self.cleaned_data['birth_latest_date'], 'end')

    def clean_death_latest_day_known(self):
        return self.clean_day(self.cleaned_data['death_latest_date'], 'end')

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


class ShortDateForm(ModelForm, DateSelectMixin):
    start_earliest_date = forms.CharField(widget=NewSelectDateWidget(
        attrs={'class': 'input-small'},
        years=YEARS), required=False)
    end_earliest_date = forms.CharField(widget=NewSelectDateWidget(
        attrs={'class': 'input-small'},
        years=YEARS), required=False)

    def clean(self):
        cleaned_data = super(ShortDateForm, self).clean()
        start_earliest_date = cleaned_data['start_earliest_date']
        cleaned_data['start_earliest_month'] = self.clean_month(start_earliest_date, 'start')
        cleaned_data['start_earliest_day'] = self.clean_day(start_earliest_date, 'start')
        cleaned_data['start_earliest_date'] = self.clean_date(start_earliest_date, 'start')
        end_earliest_date = cleaned_data['end_earliest_date']
        cleaned_data['end_earliest_month'] = self.clean_month(end_earliest_date, 'start')
        cleaned_data['end_earliest_day'] = self.clean_day(end_earliest_date, 'start')
        cleaned_data['end_earliest_date'] = self.clean_date(end_earliest_date, 'start')
        return cleaned_data


class AddEventForm(ModelForm, DateSelectMixin):
    years = [year for year in range(1850, 2013)]
    # These are CharFields so they don't get vaildated as dates
    start_earliest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=years), required=False)
    start_latest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=years), required=False)
    end_earliest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=years), required=False)
    end_latest_date = forms.CharField(widget=NewSelectDateWidget(
                                attrs={'class': 'input-small'},
                                years=years), required=False)

    def clean(self):
        cleaned_data = super(AddEventForm, self).clean()
        start_earliest_date = cleaned_data['start_earliest_date']
        start_latest_date = cleaned_data['start_latest_date']
        cleaned_data['start_earliest_month'] = self.clean_month(start_earliest_date, 'start')
        cleaned_data['start_earliest_day'] = self.clean_day(start_earliest_date, 'start')
        cleaned_data['start_latest_month'] = self.clean_month(start_latest_date, 'end')
        cleaned_data['start_latest_day'] = self.clean_day(start_latest_date, 'end')
        cleaned_data['start_earliest_date'] = self.clean_date(start_earliest_date, 'start')
        cleaned_data['start_latest_date'] = self.clean_date(start_latest_date, 'end')
        end_earliest_date = cleaned_data['end_earliest_date']
        end_latest_date = cleaned_data['end_latest_date']
        cleaned_data['end_earliest_month'] = self.clean_month(end_earliest_date, 'start')
        cleaned_data['end_earliest_day'] = self.clean_day(end_earliest_date, 'start')
        cleaned_data['end_latest_month'] = self.clean_month(end_latest_date, 'end')
        cleaned_data['end_latest_day'] = self.clean_day(end_latest_date, 'end')
        cleaned_data['end_earliest_date'] = self.clean_date(end_earliest_date, 'start')
        cleaned_data['end_latest_date'] = self.clean_date(end_latest_date, 'end')
        return cleaned_data
