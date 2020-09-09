import calendar

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class StandardMetadata(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def class_name(self):
        return self.__class__.__name__

    class Meta:
        abstract = True


class ShortDateMixin(models.Model):
    start_earliest_date = models.DateField(null=True, blank=True)
    start_earliest_month = models.BooleanField(default=False)
    start_earliest_day = models.BooleanField(default=False)
    end_earliest_date = models.DateField(null=True, blank=True)
    end_earliest_month = models.BooleanField(default=False)
    end_earliest_day = models.BooleanField(default=False)

    def formatted_date(self, date_name):
        months = calendar.month_name
        date_obj = getattr(self, '{}_date'.format(date_name))
        month = getattr(self, '{}_month'.format(date_name))
        day = getattr(self, '{}_day'.format(date_name))
        if date_obj and month and day:
            date_str = '{} {} {}'.format(date_obj.day, months[date_obj.month], date_obj.year)
        elif date_obj and month:
            date_str = '{} {}'.format(months[date_obj.month], date_obj.year)
        elif date_obj:
            date_str = str(date_obj.year)
        else:
            date_str = None
        return date_str

    def start_earliest(self):
        return self.formatted_date('start_earliest')

    def end_earliest(self):
        return self.formatted_date('end_earliest')

    class Meta:
        abstract = True


class LongDateMixin(ShortDateMixin):
    start_latest_date = models.DateField(null=True, blank=True)
    start_latest_month = models.BooleanField(default=False)
    start_latest_day = models.BooleanField(default=False)
    end_latest_date = models.DateField(null=True, blank=True)
    end_latest_month = models.BooleanField(default=False)
    end_latest_day = models.BooleanField(default=False)

    def start_latest(self):
        return self.formatted_date('start_latest')

    def end_latest(self):
        return self.formatted_date('end_latest')

    class Meta:
        abstract = True


class Thing(StandardMetadata):
    label = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.label


class Person(StandardMetadata):
    display_name = models.CharField(max_length=200, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    birth_earliest_date = models.DateField(null=True, blank=True)
    birth_earliest_month_known = models.BooleanField(default=False)
    birth_earliest_day_known = models.BooleanField(default=False)
    birth_latest_date = models.DateField(null=True, blank=True)
    birth_latest_month_known = models.BooleanField(default=False)
    birth_latest_day_known = models.BooleanField(default=False)
    death_earliest_date = models.DateField(null=True, blank=True)
    death_earliest_month_known = models.BooleanField(default=False)
    death_earliest_day_known = models.BooleanField(default=False)
    death_latest_date = models.DateField(null=True, blank=True)
    death_latest_month_known = models.BooleanField(default=False)
    death_latest_day_known = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def formatted_date(self, date_name):
        months = calendar.month_name
        date_obj = getattr(self, '{}_date'.format(date_name))
        month = getattr(self, '{}_month_known'.format(date_name))
        day = getattr(self, '{}_day_known'.format(date_name))
        if date_obj and month and day:
            date_str = '{} {} {}'.format(date_obj.day, months[date_obj.month], date_obj.year)
        elif date_obj and month:
            date_str = '{} {}'.format(months[date_obj.month], date_obj.year)
        elif date_obj:
            date_str = '{} {} {}'.format(date_obj.day, months[date_obj.month], date_obj.year)
        else:
            date_str = None
        return date_str

    def birth_earliest(self):
        return self.formatted_date('birth_earliest')

    def death_earliest(self):
        return self.formatted_date('death_earliest')

    def birth_latest(self):
        return self.formatted_date('birth_latest')

    def death_latest(self):
        return self.formatted_date('death_latest')

    def __str__(self):
        return self.display_name


class Group(StandardMetadata, ShortDateMixin):
    display_name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.display_name


class Place(StandardMetadata):
    display_name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.display_name


class Event(StandardMetadata, LongDateMixin):
    label = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.label

    class Meta:
        abstract = True


class Period(Event):
    '''Period of time.'''

    class Meta:
        abstract = True


class URI(StandardMetadata):
    URI_TYPES = (('html', 'HTML'), ('lod_id', 'LOD id'), ('rdf_xml', 'RDF/XML'), ('rdf_turtle', 'Turtle'), ('json', 'JSON'))
    uri = models.URLField()
    uri_type = models.CharField(max_length=20, choices=URI_TYPES, default='html')

    def __str__(self):
        return '%s (%s)' % (self.uri, self.uri_type)

    class Meta:
        abstract = True
