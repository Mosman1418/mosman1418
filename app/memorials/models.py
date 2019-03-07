from django.db import models
from django.urls import reverse

from app.linkeddata.models import RDFProperty
from app.generic.models import StandardMetadata


class Memorial(StandardMetadata):
    name = models.CharField(max_length=250, blank=True)
    location = models.ForeignKey('places.Place', on_delete=models.CASCADE, blank=True, null=True, related_name='memorial_location')
    description = models.TextField(blank=True)
    inscription = models.TextField(blank=True)
    address = models.ForeignKey('places.Address', on_delete=models.CASCADE, blank=True, null=True)
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
    memorial = models.ForeignKey('Memorial', on_delete=models.CASCADE)
    label = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    inscription = models.TextField(blank=True)

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('memorial-part-names-list', args=[str(self.id)])


class MemorialImage(models.Model):
    memorial = models.ForeignKey('Memorial', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='memorials')
    caption = models.TextField(blank=True)
    credit = models.CharField(max_length=250)


class MemorialName(StandardMetadata):
    memorial = models.ForeignKey('Memorial', on_delete=models.CASCADE)
    memorial_part = models.ForeignKey('MemorialPart', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=250, blank=True)
    inscription = models.TextField(blank=True)
    row = models.IntegerField(blank=True, null=True)
    column = models.IntegerField(blank=True, null=True)
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE, blank=True, null=True)
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
    memorial = models.ForeignKey('Memorial', on_delete=models.CASCADE)
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE,)
    association = models.ForeignKey('MemorialAssociation', on_delete=models.CASCADE,)

    def __unicode__(self):
        return self.person.__unicode__()


class MemorialAssociatedOrganisation(models.Model):
    memorial = models.ForeignKey('Memorial', on_delete=models.CASCADE)
    organisation = models.ForeignKey('people.Organisation', on_delete=models.CASCADE)
    association = models.ForeignKey('MemorialAssociation', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.organisation.__unicode__()


class MemorialAssociatedEvent(models.Model):
    memorial = models.ForeignKey('Memorial', on_delete=models.CASCADE)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    association = models.ForeignKey('MemorialAssociation', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.event.__unicode__()


class MemorialAssociatedPlace(models.Model):
    memorial = models.ForeignKey('Memorial', on_delete=models.CASCADE)
    place = models.ForeignKey('places.Place', on_delete=models.CASCADE)
    association = models.ForeignKey('MemorialPlaceAssociation', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.place.__unicode__()


class MemorialAssociatedObject(models.Model):
    memorial = models.ForeignKey('Memorial', on_delete=models.CASCADE)
    object = models.ForeignKey('objects.Object', on_delete=models.CASCADE)
    association = models.ForeignKey('MemorialAssociation', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.object.__unicode__()


class MemorialAssociatedSource(models.Model):
    memorial = models.ForeignKey('Memorial', on_delete=models.CASCADE)
    source = models.ForeignKey('sources.Source', on_delete=models.CASCADE)
    association = models.ForeignKey('MemorialSourceAssociation', on_delete=models.CASCADE)

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
