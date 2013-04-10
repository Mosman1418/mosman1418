from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from app.linkeddata.models import RDFClass, RDFRelationship, RDFType
from app.generic.models import StandardMetadata, Event, Period, Person as GenericPerson, Group, ShortDateMixin, LongDateMixin


class Person(GenericPerson):
    family_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, blank=True, choices=(('male', 'male'), ('female', 'female')))
    last_rank = models.CharField(max_length=50, blank=True, null=True)
    #roles = models.ManyToManyField('PersonRole')
    addresses = models.ManyToManyField('places.Address', blank=True, null=True, through='PersonAddress')
    associated_places = models.ManyToManyField('places.Place', blank=True, null=True, through='PersonAssociatedPlace')
    associated_people = models.ManyToManyField('Person', blank=True, null=True, through='PersonAssociatedPerson', related_name='related_people')
    associated_organisations = models.ManyToManyField('Organisation', blank=True, null=True, through='PersonAssociatedOrganisation')
    associated_events = models.ManyToManyField('events.Event', blank=True, null=True, through='PersonAssociatedEvent')
    associated_objects = models.ManyToManyField('objects.Object', blank=True, null=True, through='PersonAssociatedObject')
    associated_sources = models.ManyToManyField('sources.Source', blank=True, null=True, through='PersonAssociatedSource')
    images = models.ManyToManyField('PeopleImage', blank=True, null=True)
    stories = models.ManyToManyField('sources.Story', blank=True, null=True)
    public = models.BooleanField(default=False)  # Display on website
    status = models.CharField(max_length=15, choices=(
                                                ('confirmed', 'confirmed'),
                                                ('pending', 'pending'),
                                                ('rejected', 'rejected'),
                                                ('non-service', 'non-service')
                                                ))
    mosman_connection = models.TextField(blank=True, null=True)
    admin_note = models.TextField(blank=True, null=True)

    def __unicode__(self):
        if self.display_name:
            display = self.display_name
        else:
            if self.other_names:
                display = '%s %s' % (self.other_names, self.family_name)
            else:
                display = self.family_name
        return display

    def alpha_name(self):
        return '%s, %s' % (self.family_name, self.other_names)

    def main_sources(self):
        relations = (self.personassociatedsource_set
                     .filter(association__label='primary topic of'))
        return [relation.source for relation in relations]

    def other_sources(self):
        relations = (self.personassociatedsource_set
                     .filter(association__label='topic of'))
        return [relation.source for relation in relations]

    def photos(self):
        photos = (self.personassociatedsource_set
                  .filter(association__label='primary topic of')
                  .filter(source__source_type__label='photograph'))
        return [photo.source for photo in photos]

    class Meta:
        ordering = ['family_name', 'other_names']
        permissions = (('approve_person', 'Approve person'),)

    def get_absolute_url(self):
        return reverse('person-view', args=[str(self.id)])

    def class_name(self):
        return self.__class__.__name__


class Rank(StandardMetadata, ShortDateMixin):
    person = models.ForeignKey('Person')
    rank = models.CharField(max_length=100)
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True, null=True)

    def __unicode__(self):
        return '{} held rank of {}{}'.format(
                self.person,
                self.rank,
                ' ({})'.format(self.date_summary()) if self.date_summary() else ''
            )

    def summary(self):
        return 'held rank of {}{}'.format(
                self.rank,
                ' ({})'.format(self.date_summary()) if self.date_summary() else ''
            )

    def date_summary(self):
        start = self.start_earliest()
        end = self.end_earliest()
        dates = []
        if start:
            dates.append(start)
        if end:
            dates.append(end)
        if len(dates) > 0:
            summary = ' &ndash; '.join(dates)
        else:
            summary = ''
        return summary

    def get_absolute_url(self):
        return reverse('rank-view', args=[self.id])


class ServiceNumber(StandardMetadata):
    person = models.ForeignKey('Person')
    service_number = models.CharField(max_length=100)
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)

    def __unicode__(self):
        return '{}: service number {}'.format(self.person, self.service_number)

    def summary(self):
        return 'Service number {}'.format(self.service_number)

    def get_absolute_url(self):
        return reverse('servicenumber-view', args=[self.id])


class AlternativePersonName(StandardMetadata):
    person = models.ForeignKey('Person')
    family_name = models.CharField(max_length=100, blank=True)
    other_names = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=250)
    nickname = models.CharField(max_length=100, blank=True)
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True, null=True)

    def __unicode__(self):
        if self.display_name:
            display = self.display_name
        else:
            if self.other_names:
                display = '%s %s' % (self.other_names, self.family_name)
            else:
                display = self.family_name
        return display

    def get_absolute_url(self):
        return reverse('altname-view', args=[str(self.id)])

    def class_name(self):
        return self.__class__.__name__


class LifeEvent(Event):
    person = models.ForeignKey('people.Person')
    locations = models.ManyToManyField('places.Place', blank=True, null=True, through='EventLocation')
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)
    type_of_event = models.ForeignKey('people.LifeEventType', blank=True, null=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True, null=True)

    def __unicode__(self):
        return '{}: {} ({})'.format(self.person, self.label, self.date_summary())

    def summary(self):
        if self.date_summary():
            summary = '{} ({})'.format(self.label, self.date_summary())
        else:
            summary = self.label
        return summary

    def get_absolute_url(self):
        return reverse('lifeevent-view', args=[str(self.id)])

    def date_summary(self):
        start = self.start_earliest()
        end_earliest = self.end_earliest()
        end_latest = self.end_latest()
        dates = []
        if start:
            dates.append(start)
        if end_latest:
            dates.append(end_latest)
        elif end_earliest:
            dates.append(end_earliest)
        if len(dates) > 0:
            summary = ' &ndash; '.join(dates)
        else:
            summary = ''
        return summary

    def event_type(self):
        return 'events'

    def class_name(self):
        return self.__class__.__name__


class EventLocation(StandardMetadata):
    lifeevent = models.ForeignKey('people.LifeEvent')
    location = models.ForeignKey('places.Place', blank=True, null=True)
    association = models.ForeignKey('people.EventLocationAssociation', blank=True, null=True)

    def __unicode__(self):
        summary = self.lifeevent.__unicode__()
        if self.location:
            summary += ' {} {}'.format(self.association, self.location)
        return summary

    def summary(self):
        return '{} {}'.format(self.association, self.location)

    def class_name(self):
        return self.__class__.__name__


class EventLocationAssociation(RDFRelationship):
    pass


class LifePeriod(Period):
    person = models.ForeignKey('people.Person')


class Birth(Event):
    person = models.ForeignKey('people.Person')
    location = models.ForeignKey('places.Place', blank=True, null=True)
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)

    def __unicode__(self):
        earliest = self.formatted_date('start_earliest')
        latest = self.formatted_date('start_latest')
        summary = '{} born '.format(self.person)
        if earliest:
            if earliest and latest:
                summary += 'between {} and {}'.format(earliest, latest)
            elif earliest:
                summary += earliest
            if self.location:
                summary += ' in {}'.format(self.location)
        elif self.location:
            summary = 'In {}'.format(self.location.__unicode__())
        return summary

    def summary(self):
        earliest = self.formatted_date('start_earliest')
        latest = self.formatted_date('start_latest')
        if earliest:
            if earliest and latest:
                summary = 'Between {} and {}'.format(earliest, latest)
            elif earliest:
                summary = earliest
            if self.location:
                summary += ' in {}'.format(self.location)
        elif self.location:
            summary = 'In {}'.format(self.location.__unicode__())
        return summary

    def get_absolute_url(self):
        return reverse('birth-view', args=[str(self.id)])

    def event_type(self):
        return 'births'

    def class_name(self):
        return self.__class__.__name__


class Death(Event):
    person = models.ForeignKey('people.Person')
    location = models.ForeignKey('places.Place', blank=True, null=True)
    cause_of_death = models.CharField(max_length=200, blank=True, null=True)
    burial_place = models.ForeignKey('places.Place', blank=True, null=True, related_name='burial_place')
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True, null=True)

    def __unicode__(self):
        earliest = self.formatted_date('start_earliest')
        latest = self.formatted_date('start_latest')
        summary = '{} died '.format(self.person)
        if earliest:
            if earliest and latest:
                summary += 'between {} and {}'.format(earliest, latest)
            elif earliest:
                summary += earliest
        if self.location:
            summary += ' in {}'.format(self.location)
        elif self.location:
            summary = 'In {}'.format(self.location.__unicode__())
        return summary

    def summary(self):
        earliest = self.formatted_date('start_earliest')
        latest = self.formatted_date('start_latest')
        if earliest:
            if earliest and latest:
                summary = 'Between {} and {}'.format(earliest, latest)
            elif earliest:
                summary = earliest
            if self.location:
                summary += ' in {}'.format(self.location)
        elif self.location:
            summary = 'In {}'.format(self.location.__unicode__())
        elif self.burial_place:
            summary = 'Buried at {}'.format(self.burial_place)
        elif self.cause_of_death:
            summary = self.cause_of_death
        elif self.label:
            summary = self.label
        return summary

    def get_absolute_url(self):
        return reverse('death-view', args=[str(self.id)])

    def event_type(self):
        return 'deaths'

    def class_name(self):
        return self.__class__.__name__


class Family(models.Model):
    family_name = models.CharField(max_length=100)


class Organisation(Group):
    name = models.CharField(max_length=250)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    public = models.BooleanField(default=False)  # Display on website
    mosman_related = models.BooleanField(default=True)  # Appear in main people lists (not just authors)
    associated_sources = models.ManyToManyField('sources.Source', blank=True, null=True, through='OrganisationAssociatedSource')
    images = models.ManyToManyField('PeopleImage', blank=True, null=True)
    stories = models.ManyToManyField('sources.Story', blank=True, null=True)

    def __unicode__(self):
        return self.name if self.name else self.display_name


class Repository(Group):
    daa_id = models.URLField(blank=True)
    name = models.CharField(max_length=250)
    short_name = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.name if self.name else self.display_name


class PeopleImage(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images/people')
    caption = models.TextField(null=True, blank=True)
    earliest_date = models.DateField(null=True, blank=True)
    earliest_month_known = models.BooleanField(default=False)
    earliest_day_known = models.BooleanField(default=False)
    latest_date = models.DateField(null=True, blank=True)
    latest_month_known = models.BooleanField(default=False)
    latest_day_known = models.BooleanField(default=False)
    added_by = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('view_image', [str(self.id)])


class PeopleStory(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    earliest_date = models.DateField(null=True, blank=True)
    earliest_month_known = models.BooleanField(default=False)
    earliest_day_known = models.BooleanField(default=False)
    latest_date = models.DateField(null=True, blank=True)
    latest_month_known = models.BooleanField(default=False)
    latest_day_known = models.BooleanField(default=False)
    added_by = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('view_story', [str(self.id)])


class PersonRole(RDFRelationship):
    pass


class PersonAddress(StandardMetadata, ShortDateMixin):
    person = models.ForeignKey('Person')
    address = models.ForeignKey('places.Address')
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)

    def __unicode__(self):
        return '{} lived at {}'.format(self.person, self.address)

    def summary(self):
        return 'lived at {}'.format(self.address)

    def class_name(self):
        return self.__class__.__name__


class PersonAssociatedPlace(models.Model):
    person = models.ForeignKey('Person')
    place = models.ForeignKey('places.Place')
    association = models.ForeignKey('PersonAssociation')


class PersonAssociatedPerson(StandardMetadata, ShortDateMixin):
    person = models.ForeignKey('Person')
    associated_person = models.ForeignKey('Person', related_name='related_person', blank=True, null=True)
    association = models.ForeignKey('PersonAssociation')
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)

    def __unicode__(self):
        if self.associated_person:
            summary = '{} {} {}'.format(self.person, self.association, self.associated_person)
        else:
            summary = '{} {}'.format(self.person, self.association)
        return summary

    def summary(self):
        return '{} &ndash; {}'.format(self.association, self.associated_person)

    def class_name(self):
        return self.__class__.__name__

    def get_absolute_url(self):
        return reverse('person-relationship-view', args=[str(self.id)])


class PersonAssociatedOrganisation(StandardMetadata, ShortDateMixin):
    person = models.ForeignKey('Person')
    organisation = models.ForeignKey('Organisation')
    association = models.ForeignKey('PersonOrgAssociation', null=True, blank=True)
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True, null=True)

    def __unicode__(self):
        if self.organisation:
            summary = '{} {} {}'.format(self.person, self.association, self.organisation)
        else:
            summary = '{} {}'.format(self.person, self.association)
        return summary

    def summary(self):
        return '{} &ndash; {}'.format(self.association, self.organisation)

    def get_absolute_url(self):
        return reverse('personorganisation-view', args=[str(self.id)])


class PersonAssociatedObject(models.Model):
    person = models.ForeignKey('Person')
    object = models.ForeignKey('objects.Object')
    association = models.ForeignKey('PersonAssociation')


class PersonAssociatedEvent(models.Model):
    person = models.ForeignKey('Person')
    event = models.ForeignKey('events.Event')
    association = models.ForeignKey('EventAssociation')


class PersonAssociatedSource(StandardMetadata):
    person = models.ForeignKey('Person')
    source = models.ForeignKey('sources.Source')
    association = models.ForeignKey('SourceAssociation')


class PersonAssociation(RDFRelationship):
    pass


class SourceAssociation(RDFRelationship):
    pass


class EventAssociation(RDFRelationship):
    pass


class OrgAssociation(RDFRelationship):
    pass


class PersonOrgAssociation(RDFRelationship):
    pass


class ObjectAssociation(RDFRelationship):
    pass


class OrganisationAssociatedSource(StandardMetadata):
    organisation = models.ForeignKey('Organisation')
    source = models.ForeignKey('sources.Source')
    association = models.ForeignKey('SourceAssociation')


class LifeEventType(RDFType):
    ''' Tyep of life event '''
    pass
