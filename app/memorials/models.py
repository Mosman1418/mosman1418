from django.db import models

from app.places.models import Place
from app.people.models import Person, Organisation
from app.events.models import Event
from app.objects.models import Object
from app.sources.models import Source

# Create your models here.


class Memorial(models.Model):
    name = models.CharField(max_length=250, blank=True)
    location = models.ForeignKey(Place, blank=True, null=True, related_name='memorial_location')
    description = models.TextField(blank=True)
    inscription = models.TextField(blank=True)
    associated_people = models.ManyToManyField(Person, through='MemorialAssociatedPerson')
    associated_organisations = models.ManyToManyField(Organisation, through='MemorialAssociatedOrganisation')
    associated_places = models.ManyToManyField(Place, through='MemorialAssociatedPlace')
    associated_events = models.ManyToManyField(Event, through='MemorialAssociatedEvent')
    associated_objects = models.ManyToManyField(Object, through='MemorialAssociatedObject')
    associated_sources = models.ManyToManyField(Source, through='MemorialAssociatedSource')

    def __unicode__(self):
        return self.name


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
    person = models.ForeignKey(Person, blank=True, null=True)

    def __unicode__(self):
        return self.name


class MemorialAssociatedPerson(models.Model):
    memorial = models.ForeignKey('Memorial')
    person = models.ForeignKey(Person)
    association = models.ForeignKey('MemorialAssociation')


class MemorialAssociatedOrganisation(models.Model):
    memorial = models.ForeignKey('Memorial')
    person = models.ForeignKey(Organisation)
    association = models.ForeignKey('MemorialAssociation')


class MemorialAssociatedEvent(models.Model):
    memorial = models.ForeignKey('Memorial')
    event = models.ForeignKey(Event)
    association = models.ForeignKey('MemorialAssociation')


class MemorialAssociatedPlace(models.Model):
    memorial = models.ForeignKey('Memorial')
    person = models.ForeignKey(Place)
    association = models.ForeignKey('MemorialAssociation')


class MemorialAssociatedObject(models.Model):
    memorial = models.ForeignKey('Memorial')
    source = models.ForeignKey(Object)
    association = models.ForeignKey('MemorialAssociation')


class MemorialAssociatedSource(models.Model):
    memorial = models.ForeignKey('Memorial')
    source = models.ForeignKey(Source)
    association = models.ForeignKey('MemorialAssociation')

    def __unicode__(self):
        return '%s: %s (%s) %s' % (self.association, self.source, self.source.source_type, self.source.url)


class MemorialAssociation(models.Model):
    association = models.CharField(max_length=250, blank=True)
    rdf_property = models.CharField(max_length=250, blank=True)

    def __unicode__(self):
        return self.association
