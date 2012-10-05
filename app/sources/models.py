from django.db import models

from app.linkeddata.models import RDFClass, RDFProperty

# Create your models here.


class Source(models.Model):
    title = models.CharField(max_length=250, blank=True, null=True)
    source_type = models.ForeignKey('SourceType')  # include rdf?
    creators = models.ManyToManyField('people.Person', through='SourcePerson', blank=True, null=True)
    publisher = models.ForeignKey('people.Organisation', blank=True, null=True, related_name='publisher_source')
    publication_place = models.CharField(max_length=100, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    publication_date_month = models.BooleanField(default=False)
    publication_date_day = models.BooleanField(default=False)
    publication_date_end = models.DateField(blank=True, null=True)
    publication_date_end_month = models.BooleanField(default=False)
    publication_date_end_day = models.BooleanField(default=False)
    collection = models.ForeignKey('Source', blank=True, null=True, related_name='collection_source')
    collection_title = models.CharField(max_length=250, blank=True, null=True)
    collection_item_id = models.CharField(max_length=100, blank=True, null=True)  # Identifier within context of a specific collection, eg file number
    repository_item_id = models.CharField(max_length=100, blank=True, null=True)  # Identifier within context of repository, eg barcode
    repository = models.ForeignKey('people.Organisation', blank=True, null=True, related_name='repository_source')
    citation = models.CharField(max_length=250, blank=True, null=True)
    pages = models.CharField(max_length=50, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    rdf_url = models.URLField(blank=True, null=True)
    json_url = models.URLField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('source_view', [str(self.id)])


class SourcePerson(models.Model):
    source = models.ForeignKey(Source)
    person = models.ForeignKey('people.Person')
    role = models.ForeignKey('SourceRole')

    def __unicode__(self):
        return '%s - %s - %s' % (self.source, self.role, self.person)


class SourceRole(models.Model):
    label = models.CharField(max_length=50)
    rdf_property = models.ManyToManyField(RDFProperty, blank=True, null=True)

    def __unicode__(self):
        return self.label


class SourceType(models.Model):
    label = models.CharField(max_length=50)
    rdf_class = models.ManyToManyField(RDFClass, blank=True, null=True)

    def __unicode__(self):
        return self.label
