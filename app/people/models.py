from django.db import models
from django.contrib.auth.models import User
from app.linkeddata.models import RDFProperty


class Person(models.Model):
    family_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=250, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    #roles = models.ManyToManyField('PersonRole')
    addresses = models.ManyToManyField('places.Address', blank=True, null=True, through='PersonAddress')
    associated_places = models.ManyToManyField('places.Place', blank=True, null=True, through='PersonAssociatedPlace')
    associated_people = models.ManyToManyField('Person', blank=True, null=True, through='PersonAssociatedPerson', related_name='related_people')
    associated_organisations = models.ManyToManyField('Organisation', blank=True, null=True, through='PersonAssociatedOrganisation')
    associated_events = models.ManyToManyField('events.Event', blank=True, null=True, through='PersonAssociatedEvent')
    associated_objects = models.ManyToManyField('objects.Object', blank=True, null=True, through='PersonAssociatedObject')
    associated_sources = models.ManyToManyField('sources.Source', blank=True, null=True, through='PersonAssociatedSource')
    images = models.ManyToManyField('PeopleImage', blank=True, null=True)
    stories = models.ManyToManyField('PeopleStory', blank=True, null=True)
    public = models.BooleanField(default=False)  # Display on website
    mosman_related = models.BooleanField(default=True)  # Appear in main people lists (not just authors)

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

    class Meta:
        ordering = ['family_name', 'other_names']

    @models.permalink
    def get_absolute_url(self):
        return ('person_view', [str(self.id)])


class AlternativePersonName(models.Model):
    person = models.ForeignKey('Person')
    family_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=250, blank=True)
    nickname = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        if self.display_name:
            display = self.display_name
        else:
            if self.other_names:
                display = '%s %s' % (self.other_names, self.family_name)
            else:
                display = self.family_name
        return display


class Family(models.Model):
    family_name = models.CharField(max_length=100)


class Organisation(models.Model):
    name = models.CharField(max_length=250)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    public = models.BooleanField(default=False)  # Display on website
    mosman_related = models.BooleanField(default=True)  # Appear in main people lists (not just authors)
    associated_sources = models.ManyToManyField('sources.Source', blank=True, null=True, through='OrganisationAssociatedSource')
    images = models.ManyToManyField('PeopleImage', blank=True, null=True)
    stories = models.ManyToManyField('PeopleStory', blank=True, null=True)

    def __unicode__(self):
        return self.name


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


class PersonRole(models.Model):
    label = models.CharField(max_length=50)
    rdf_property = models.ManyToManyField(RDFProperty, blank=True, null=True)


class PersonAddress(models.Model):
    person = models.ForeignKey('Person')
    address = models.ForeignKey('places.Address')
    start_date = models.DateField(blank=True, null=True)
    start_date_month = models.BooleanField(default=False)
    start_date_day = models.BooleanField(default=False)
    end_date = models.DateField(blank=True, null=True)
    end_date_month = models.BooleanField(default=False)
    end_date_day = models.BooleanField(default=False)
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)


class PersonAssociatedPlace(models.Model):
    person = models.ForeignKey('Person')
    place = models.ForeignKey('places.Place')
    association = models.ForeignKey('PersonAssociation')


class PersonAssociatedPerson(models.Model):
    person = models.ForeignKey('Person')
    associated_person = models.ForeignKey('Person', related_name='related_person')
    association = models.ForeignKey('PersonAssociation')


class PersonAssociatedOrganisation(models.Model):
    person = models.ForeignKey('Person')
    organisation = models.ForeignKey('Organisation')
    association = models.ForeignKey('PersonAssociation')


class PersonAssociatedObject(models.Model):
    person = models.ForeignKey('Person')
    object = models.ForeignKey('objects.Object')
    association = models.ForeignKey('PersonAssociation')


class PersonAssociatedEvent(models.Model):
    person = models.ForeignKey('Person')
    event = models.ForeignKey('events.Event')
    association = models.ForeignKey('PersonAssociation')


class PersonAssociatedSource(models.Model):
    person = models.ForeignKey('Person')
    event = models.ForeignKey('sources.Source')
    association = models.ForeignKey('PersonAssociation')


class PersonAssociation(models.Model):
    label = models.CharField(max_length=50)
    rdf_property = models.ManyToManyField(RDFProperty, blank=True, null=True)

    def __unicode__(self):
        return self.label


class OrganisationAssociatedSource(models.Model):
    organisation = models.ForeignKey('Organisation')
    source = models.ForeignKey('sources.Source')
    association = models.ForeignKey('PersonAssociation')
