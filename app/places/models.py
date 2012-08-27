from django.db import models

# Create your models here.

class Place(models.Model):
    name = models.CharField(max_length=250, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    
    
class Address(models.Model):
    street_name = models.CharField(max_length=250, blank=True)
    street_number = models.CharField(max_length=250, blank=True)
    