from django.db import models
from django.core.urlresolvers import reverse

from app.generic.models import Place as GenericPlace, StandardMetadata

# Create your models here.


class Place(GenericPlace):
    place_name = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    geonames_id = models.IntegerField(blank=True, null=True)
    sources = models.ManyToManyField('sources.Source', blank=True, null=True)
    merged_into = models.ForeignKey('places.Place', blank=True, null=True)

    def __unicode__(self):
        if not self.place_name:
            summary = self.display_name
        else:
            summary = '{}{}{}'.format(
                self.place_name,
                ', {}'.format(self.state) if self.state else '',
                ', {}'.format(self.country) if self.country else ''
            )
        return summary

    def get_absolute_url(self):
        return reverse('place-view', args=[self.id])

    def burial_places(self):
        people = list(set(self.burial_place.values_list('person__family_name', 'person__other_names', 'person')))
        return people

    def death_places(self):
        people = list(set(self.death_set.values_list('person__family_name', 'person__other_names', 'person')))
        return people

    def birth_places(self):
        people = list(set(self.birth_set.values_list('person__family_name', 'person__other_names', 'person')))
        return people

    class Meta:
        ordering = ['place_name']
        permissions = [('merge_place', 'Merge place')]


class Address(StandardMetadata):
    building_name = models.CharField(max_length=250, blank=True)
    street_name = models.CharField(max_length=250, blank=True)
    street_number = models.CharField(max_length=250, blank=True)
    mosman_street = models.ForeignKey('places.MosmanStreet', null=True, blank=True)
    place = models.ForeignKey('places.Place', null=True, blank=True)

    def __unicode__(self):
        if self.mosman_street:
            street = self.mosman_street.street_name.strip()
        elif self.street_name:
            street = self.street_name
        else:
            street = None
        return '{building}{number}{street}, {place}'.format(
            building='{}, '.format(self.building_name) if self.building_name else '',
            number='{} '.format(self.street_number) if self.street_number else '',
            street='{}'.format(street if street else ''),
            place=self.place
        )

    class Meta:
        ordering = ['street_name', 'mosman_street__street_name', 'street_number']

    def get_absolute_url(self):
        return reverse('address-view', args=[self.id])


class MosmanStreet(models.Model):
    street_name = models.CharField(max_length=250, blank=True)
    bounding_box = models.CharField(max_length=250, blank=True)

    def __unicode__(self):
        return self.street_name

    def get_absolute_url(self):
        return reverse('mosmanstreet-view', args=[self.id])
