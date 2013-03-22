import calendar

from django.db import models
from django.core.urlresolvers import reverse

from app.linkeddata.models import RDFClass, RDFRelationship, RDFType
from app.generic.models import StandardMetadata

# Create your models here.


class Source(StandardMetadata):
    title = models.TextField(blank=True, null=True)
    source_type = models.ForeignKey('SourceType')  # include rdf?
    creators = models.ManyToManyField('people.Person', through='SourcePerson', blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    publication_place = models.CharField(max_length=100, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    publication_date_month_known = models.BooleanField(default=False)
    publication_date_day_known = models.BooleanField(default=False)
    publication_date_end = models.DateField(blank=True, null=True)
    publication_date_end_month_known = models.BooleanField(default=False)
    publication_date_end_day_known = models.BooleanField(default=False)
    collection = models.ForeignKey('Source', blank=True, null=True, related_name='collection_source')
    collection_title = models.CharField(max_length=250, blank=True, null=True)
    collection_item_id = models.CharField(max_length=100, blank=True, null=True)  # Identifier within context of a specific collection, eg file number
    repository_item_id = models.CharField(max_length=100, blank=True, null=True)  # Identifier within context of repository, eg barcode
    repository = models.ForeignKey('people.Repository', blank=True, null=True)
    citation = models.CharField(max_length=250, blank=True, null=True)
    pages = models.CharField(max_length=50, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    rdf_url = models.URLField(blank=True, null=True)
    json_url = models.URLField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    def authors(self):
        creators = self.sourceperson_set.filter(role__label='author')
        return [creator.person for creator in creators]

    def editors(self):
        creators = self.sourceperson_set.filter(role__label='editor')
        return [creator.person for creator in creators]

    def main_people(self):
        relations = self.personassociatedsource_set.filter(association__label='primary topic of')
        return [relation.person for relation in relations]

    def other_people(self):
        relations = self.personassociatedsource_set.filter(association__label='topic of')
        return [relation.person for relation in relations]

    def formatted_date(self, date_name):
        months = calendar.month_name
        date_obj = getattr(self, '{}'.format(date_name))
        month = getattr(self, '{}_month_known'.format(date_name))
        day = getattr(self, '{}_day_known'.format(date_name))
        if date_obj and month and day:
            date_str = '{} {} {}'.format(date_obj.day, months[date_obj.month], date_obj.year)
        elif date_obj and month:
            date_str = '{} {}'.format(months[date_obj.month], date_obj.year)
        elif date_obj:
            date_str = date_obj.year
        else:
            date_str = None
        return date_str

    def start_date(self):
        return self.formatted_date('publication_date')

    def end_date(self):
        return self.formatted_date('publication_date_end')

    def display_publisher(self):
        publisher = None
        if self.publisher:
            publisher = self.publisher
        elif self.collection and self.collection.publisher:
            publisher = self.collection.publisher
        return publisher

    def get_absolute_url(self):
        return reverse('source-view', args=[str(self.id)])


class SourcePerson(models.Model):
    source = models.ForeignKey(Source)
    person = models.ForeignKey('people.Person')
    role = models.ForeignKey('SourceRole')

    def __unicode__(self):
        return '%s - %s - %s' % (self.source, self.role, self.person)


class SourceRole(RDFRelationship):
    pass


class SourceType(RDFType):
    pass
