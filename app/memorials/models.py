from django.db import models
from django.core.urlresolvers import reverse

from app.linkeddata.models import RDFProperty
from app.generic.models import StandardMetadata


class Memorial(StandardMetadata):
    name = models.CharField(max_length=250, blank=True)
    location = models.ForeignKey('places.Place', blank=True, null=True, related_name='memorial_location')
    description = models.TextField(blank=True)
    inscription = models.TextField(blank=True)
    address = models.ForeignKey('places.Address', blank=True, null=True)
    associated_people = models.ManyToManyField('people.Person', through='MemorialAssociatedPerson')
    associated_organisations = models.ManyToManyField('people.Organisation', through='MemorialAssociatedOrganisation')
    associated_places = models.ManyToManyField('places.Place', through='MemorialAssociatedPlace')
    associated_events = models.ManyToManyField('events.Event', through='MemorialAssociatedEvent')
    associated_objects = models.ManyToManyField('objects.Object', through='MemorialAssociatedObject')
    associated_sources = models.ManyToManyField('sources.Source', through='MemorialAssociatedSource')

    def __unicode__(self):
        return self.name

    def main_sources(self):
        relations = (self.memorialassociatedsource_set
                     .filter(association__label='primary topic of'))
        return [relation.source for relation in relations]

    def other_sources(self):
        relations = (self.memorialassociatedsource_set
                     .filter(association__label='topic of'))
        return [relation.source for relation in relations]

    def photos(self):
        photos = (self.memorialassociatedsource_set
                  .filter(association__label='primary topic of')
                  .filter(source__source_type__label='photograph'))
        return [photo.source for photo in photos]

    def get_absolute_url(self):
        return reverse('memorial-view', args=[str(self.id)])


class MemorialPart(StandardMetadata):
    memorial = models.ForeignKey('Memorial')
    label = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    inscription = models.TextField(blank=True)

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('memorial-part-names-list', args=[str(self.id)])


class MemorialImage(models.Model):
    memorial = models.ForeignKey('Memorial')
    image = models.ImageField(upload_to='memorials')
    caption = models.TextField(blank=True)
    credit = models.CharField(max_length=250)


class MemorialName(StandardMetadata):
    memorial = models.ForeignKey('Memorial')
    memorial_part = models.ForeignKey('MemorialPart', blank=True, null=True)
    name = models.CharField(max_length=250, blank=True)
    inscription = models.TextField(blank=True)
    row = models.IntegerField(blank=True, null=True)
    column = models.IntegerField(blank=True, null=True)
    person = models.ForeignKey('people.Person', blank=True, null=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def position(self):
        position = []
        if self.row:
            position.append('row {}'.format(self.row))
        if self.column:
            position.append('column {}'.format(self.column))
        return ', '.join(position)


class MemorialAssociatedPerson(models.Model):
    memorial = models.ForeignKey('Memorial')
    person = models.ForeignKey('people.Person')
    association = models.ForeignKey('MemorialAssociation')

    def __unicode__(self):
        return self.person.__unicode__()


class MemorialAssociatedOrganisation(models.Model):
    memorial = models.ForeignKey('Memorial')
    organisation = models.ForeignKey('people.Organisation')
    association = models.ForeignKey('MemorialAssociation')

    def __unicode__(self):
        return self.organisation.__unicode__()


class MemorialAssociatedEvent(models.Model):
    memorial = models.ForeignKey('Memorial')
    event = models.ForeignKey('events.Event')
    association = models.ForeignKey('MemorialAssociation')

    def __unicode__(self):
        return self.event.__unicode__()


class MemorialAssociatedPlace(models.Model):
    memorial = models.ForeignKey('Memorial')
    place = models.ForeignKey('places.Place')
    association = models.ForeignKey('MemorialPlaceAssociation')

    def __unicode__(self):
        return self.place.__unicode__()


class MemorialAssociatedObject(models.Model):
    memorial = models.ForeignKey('Memorial')
    object = models.ForeignKey('objects.Object')
    association = models.ForeignKey('MemorialAssociation')

    def __unicode__(self):
        return self.object.__unicode__()


class MemorialAssociatedSource(models.Model):
    memorial = models.ForeignKey('Memorial')
    source = models.ForeignKey('sources.Source')
    association = models.ForeignKey('MemorialSourceAssociation')

    def __unicode__(self):
        return self.source.__unicode__()


class MemorialSourceAssociation(models.Model):
    label = models.CharField(max_length=50, blank=True, null=True)
    rdf_property = models.ManyToManyField(RDFProperty, blank=True)

    def __unicode__(self):
        return self.label


class MemorialPlaceAssociation(models.Model):
    label = models.CharField(max_length=50, blank=True, null=True)
    rdf_property = models.ManyToManyField(RDFProperty, blank=True)

    def __unicode__(self):
        return self.label


class MemorialAssociation(models.Model):
    label = models.CharField(max_length=50, blank=True, null=True)
    rdf_property = models.ManyToManyField(RDFProperty, blank=True)

    def __unicode__(self):
        return self.label
