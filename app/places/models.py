from django.db import models

from app.generic.models import Place

# Create your models here.


class Place(Place):
    place_name = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    geonames_id = models.URLField(blank=True)


class Address(models.Model):
    street_name = models.CharField(max_length=250, blank=True)
    street_number = models.CharField(max_length=250, blank=True)

