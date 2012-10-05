from django.db import models

from app.linkeddata.models import RDFProperty


class Memorial(models.Model):
    name = models.CharField(max_length=250, blank=True)
    location = models.ForeignKey('places.Place', blank=True, null=True, related_name='memorial_location')
    description = models.TextField(blank=True)
    inscription = models.TextField(blank=True)
    associated_people = models.ManyToManyField('people.Person', through='MemorialAssociatedPerson')
    associated_organisations = models.ManyToManyField('people.Organisation', through='MemorialAssociatedOrganisation')
    associated_places = models.ManyToManyField('places.Place', through='MemorialAssociatedPlace')
    associated_events = models.ManyToManyField('events.Event', through='MemorialAssociatedEvent')
    associated_objects = models.ManyToManyField('objects.Object', through='MemorialAssociatedObject')
    associated_sources = models.ManyToManyField('sources.Source', through='MemorialAssociatedSource')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('memorial_view', [str(self.id)])


class MemorialPart(models.Model):
    memorial = models.ForeignKey('Memorial')
    label = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    inscription = models.TextField(blank=True)

    def __unicode__(self):
        return self.label


class MemorialImage(models.Model):
    memorial = models.ForeignKey('Memorial')
    image = models.ImageField(upload_to='memorials')
    caption = models.TextField(blank=True)
    credit = models.CharField(max_length=250)


class MemorialName(models.Model):
    memorial = models.ForeignKey('Memorial')
    memorial_part = models.ForeignKey('MemorialPart', blank=True, null=True)
    name = models.CharField(max_length=250, blank=True)
    inscription = models.TextField(blank=True)
    row = models.IntegerField(blank=True, null=True)
    column = models.IntegerField(blank=True, null=True)
    person = models.ForeignKey('people.Person', blank=True, null=True)

    def __unicode__(self):
        return self.name


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
    association = models.ForeignKey('MemorialAssociation')

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
    association = models.ForeignKey('MemorialAssociation')

    def __unicode__(self):
        return self.source.__unicode__()


class MemorialAssociation(models.Model):
    label = models.CharField(max_length=50, blank=True, null=True)
    rdf_property = models.ManyToManyField(RDFProperty, blank=True)

    def __unicode__(self):
        return self.label
