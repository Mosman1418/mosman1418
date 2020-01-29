import re
from itertools import chain
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from app.linkeddata.models import RDFClass, RDFRelationship, RDFType
from app.generic.models import StandardMetadata, Event, Period, Person as GenericPerson, Group, ShortDateMixin, LongDateMixin


class Person(GenericPerson):
    family_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, blank=True, choices=(('male', 'male'), ('female', 'female')))
    last_rank = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    #roles = models.ManyToManyField('PersonRole')
    addresses = models.ManyToManyField('places.Address', blank=True,through='PersonAddress')
    associated_places = models.ManyToManyField('places.Place', blank=True,through='PersonAssociatedPlace')
    associated_people = models.ManyToManyField('Person', blank=True, through='PersonAssociatedPerson', related_name='related_people')
    associated_organisations = models.ManyToManyField('Organisation', blank=True,  through='PersonAssociatedOrganisation')
    associated_events = models.ManyToManyField('events.Event', blank=True, through='PersonAssociatedEvent')
    associated_objects = models.ManyToManyField('objects.Object', blank=True, through='PersonAssociatedObject')
    associated_sources = models.ManyToManyField('sources.Source', blank=True, through='PersonAssociatedSource')
    images = models.ManyToManyField('PeopleImage', blank=True)
    stories = models.ManyToManyField('sources.Story', blank=True)
    public = models.BooleanField(default=False)  # Display on website
    status = models.CharField(max_length=15, choices=(
        ('confirmed', 'confirmed'),
        ('pending', 'pending'),
        ('rejected', 'rejected'),
        ('non-service', 'non-service')
    ))
    mosman_connection = models.TextField(blank=True, null=True)
    admin_note = models.TextField(blank=True, null=True)
    merged_into = models.ForeignKey('people.Person', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.family_name:
            if self.other_names:
                display = '%s %s' % (self.other_names, self.family_name)
            else:
                display = self.family_name
        elif self.display_name:
            display = self.display_name
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

    def relationships(self):
        forward_relations = self.personassociatedperson_set.all()
        reverse_relations = self.related_person.all()
        relations = list(chain(forward_relations, reverse_relations))
        return relations

    def date_summary(self):
        start = self.birth_earliest()
        end = self.death_earliest()
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

    def birth_date_summary(self):
        if self.birth_latest_date:
            summary = 'Between {} and {}'.format(self.birth_earliest(), self.birth_latest())
        elif self.birth_earliest_date:
            summary = self.birth_earliest()
        else:
            summary = ''
        return summary

    def death_date_summary(self):
        if self.death_latest_date:
            summary = 'Between {} and {}'.format(self.death_earliest(), self.death_latest())
        elif self.death_earliest_date:
            summary = self.death_earliest()
        else:
            summary = ''
        return summary

    class Meta:
        ordering = ['family_name', 'other_names']
        permissions = (('approve_person', 'Approve person'), ('merge_person', 'Merge person'))

    def get_absolute_url(self):
        return reverse('person-view', args=[str(self.id)])

    def class_name(self):
        return self.__class__.__name__


class Rank(StandardMetadata, ShortDateMixin):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    rank = models.CharField(max_length=100)
    #sources = models.ManyToManyField('sources.Source', blank=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True)

    def __str__(self):
        return '{} held rank of {}{}'.format(
            self.person,
            self.rank,
            ' ({})'.format(self.date_summary()) if self.date_summary() else ''
        )

    def summary(self):
        return 'Held rank of {}{}'.format(
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
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    service_number = models.CharField(max_length=100)
    #sources = models.ManyToManyField('sources.Source', blank=True)

    def __str__(self):
        return '{} had service number {}'.format(self.person, self.service_number)

    def summary(self):
        return 'Service number {}'.format(self.service_number)

    def get_absolute_url(self):
        return reverse('servicenumber-view', args=[self.id])


class AlternativePersonName(StandardMetadata):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    family_name = models.CharField(max_length=100, blank=True)
    other_names = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=250)
    nickname = models.CharField(max_length=100, blank=True)
    #sources = models.ManyToManyField('sources.Source', blank=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True)

    def __str__(self):
        display = 'Recorded name &ndash; '
        if not self.display_name:
            if self.other_names:
                display += '{} {}'.format(self.other_names, self.family_name)
            else:
                display += self.family_name
        else:
            display += self.display_name
        return display

    def summary(self):
        if not self.display_name:
            if self.other_names:
                display = '{} {}'.format(self.other_names, self.family_name)
            else:
                display = self.family_name
        else:
            display = self.display_name
        return display

    def get_absolute_url(self):
        return reverse('altname-view', args=[str(self.id)])

    def class_name(self):
        return self.__class__.__name__


class LifeEvent(Event):
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE)
    locations = models.ManyToManyField('places.Place', blank=True, through='EventLocation')
    #sources = models.ManyToManyField('sources.Source', blank=True)
    type_of_event = models.ForeignKey('people.LifeEventType', on_delete=models.CASCADE, blank=True, null=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True)

    def __str__(self):
        return '{} {} {}'.format(
            self.person,
            '{}{}'.format()  if self.label[0] else '',
            '({})'.format(self.date_summary()) if self.date_summary() else ''
        )

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
    lifeevent = models.ForeignKey('people.LifeEvent', on_delete=models.CASCADE)
    location = models.ForeignKey('places.Place', on_delete=models.CASCADE, blank=True, null=True)
    association = models.ForeignKey('people.EventLocationAssociation', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        summary = self.lifeevent.__str__()
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
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE)


class Birth(Event):
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE)
    location = models.ForeignKey('places.Place', on_delete=models.CASCADE, blank=True, null=True)
    #sources = models.ManyToManyField('sources.Source', blank=True)

    def __str__(self):
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
            summary += ' in {}'.format(self.location.__str__())
        return summary

    def summary(self):
        earliest = self.formatted_date('start_earliest')
        latest = self.formatted_date('start_latest')
        summary = 'Born '
        if earliest:
            if earliest and latest:
                summary += 'between {} and {}'.format(earliest, latest)
            elif earliest:
                summary = earliest
            if self.location:
                summary += ' in {}'.format(self.location)
        elif self.location:
            summary += 'in {}'.format(self.location.__str__())
        return summary

    def get_absolute_url(self):
        return reverse('birth-view', args=[str(self.id)])

    def event_type(self):
        return 'births'

    def class_name(self):
        return self.__class__.__name__


class Death(Event):
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE)
    location = models.ForeignKey('places.Place', on_delete=models.CASCADE, blank=True, null=True)
    cause_of_death = models.CharField(max_length=200, blank=True, null=True)
    burial_place = models.ForeignKey('places.Place', on_delete=models.CASCADE, blank=True, null=True, related_name='burial_place')
    #sources = models.ManyToManyField('sources.Source', blank=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True)

    def __str__(self):
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
            summary = 'In {}'.format(self.location.__str__())
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
            summary = 'In {}'.format(self.location.__str__())
        elif self.burial_place:
            summary = 'Buried at {}'.format(self.burial_place)
        elif self.cause_of_death:
            summary = self.cause_of_death
        elif self.label:
            summary = self.label
        if summary == None:
            return ''
        else:
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
    associated_sources = models.ManyToManyField('sources.Source', blank=True, through='OrganisationAssociatedSource')
    stories = models.ManyToManyField('sources.Story', blank=True)
    merged_into = models.ForeignKey('people.Organisation', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name if self.name else self.display_name

    def get_absolute_url(self):
        return reverse('organisation-view', args=[self.id])

    def main_sources(self):
        relations = (self.organisationassociatedsource_set
                     .filter(association__label='primary topic of'))
        return [relation.source for relation in relations]

    def other_sources(self):
        relations = (self.organisationassociatedsource_set
                     .filter(association__label='topic of'))
        return [relation.source for relation in relations]

    class Meta:
        ordering = ['name']
        permissions = [('merge_organisation', 'Merge organisation')]


class Repository(Group):
    daa_id = models.URLField(blank=True)
    name = models.CharField(max_length=250)
    short_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
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
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('view_image', args=(str(self.id),))


class PeopleStory(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    earliest_date = models.DateField(null=True, blank=True)
    earliest_month_known = models.BooleanField(default=False)
    earliest_day_known = models.BooleanField(default=False)
    latest_date = models.DateField(null=True, blank=True)
    latest_month_known = models.BooleanField(default=False)
    latest_day_known = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('view_story', args=(str(self.id),))


class PersonRole(RDFRelationship):
    pass


class PersonAddress(StandardMetadata, ShortDateMixin):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    address = models.ForeignKey('places.Address', on_delete=models.CASCADE)
    #sources = models.ManyToManyField('sources.Source', blank=True)

    def __str__(self):
        return '{} lived at {}'.format(self.person, self.address)

    def summary(self):
        return 'lived at {}'.format(self.address)

    def class_name(self):
        return self.__class__.__name__

    def get_absolute_url(self):
        return reverse('personaddress-view', args=[self.id])


class PersonAssociatedPlace(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    place = models.ForeignKey('places.Place', on_delete=models.CASCADE)
    association = models.ForeignKey('PersonAssociation', on_delete=models.CASCADE)


class PersonAssociatedPerson(StandardMetadata, ShortDateMixin):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    associated_person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='related_person', blank=True, null=True)
    association = models.ForeignKey('PersonAssociation', on_delete=models.CASCADE)
    #sources = models.ManyToManyField('sources.Source', blank=True)

    def __str__(self):
        if self.associated_person:
            summary = '{} - {} {}'.format(self.person, self.association, self.associated_person)
        else:
            summary = '{} {}'.format(self.person, self.association)
        return summary

    def summary(self):
        return '{} - {}'.format(self.association, self.associated_person)

    def class_name(self):
        return self.__class__.__name__

    def get_absolute_url(self):
        return reverse('person-relationship-view', args=[str(self.id)])


class PersonAssociatedOrganisation(StandardMetadata, ShortDateMixin):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    association = models.ForeignKey('PersonOrgAssociation', on_delete=models.CASCADE, null=True, blank=True)
    #sources = models.ManyToManyField('sources.Source', blank=True)
    memorials = models.ManyToManyField('memorials.Memorial', blank=True)

    def __str__(self):
        if self.organisation:
            summary = '{} {} {}'.format(self.person, self.association, self.organisation)
        else:
            summary = '{} {}'.format(self.person, self.association)
        return summary

    def summary(self):
        if self.association:
            summary = '{} &ndash; {}'.format(self.association.label.title(), self.organisation)
        else:
            summary = self.organisation
        return summary

    def get_absolute_url(self):
        return reverse('person-membership-view', args=[str(self.id)])


class PersonAssociatedObject(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    object = models.ForeignKey('objects.Object', on_delete=models.CASCADE)
    association = models.ForeignKey('PersonAssociation', on_delete=models.CASCADE)


class PersonAssociatedEvent(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    association = models.ForeignKey('EventAssociation', on_delete=models.CASCADE)


class PersonAssociatedSource(StandardMetadata):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    source = models.ForeignKey('sources.Source', on_delete=models.CASCADE)
    association = models.ForeignKey('SourceAssociation', on_delete=models.CASCADE)


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
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    source = models.ForeignKey('sources.Source', on_delete=models.CASCADE)
    association = models.ForeignKey('SourceAssociation', on_delete=models.CASCADE)


class LifeEventType(RDFType):
    ''' Tyep of life event '''
    pass
