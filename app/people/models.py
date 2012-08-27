from django.db import models

# Create your models here.

class Person(models.Model):
    family_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=250, blank=True)
    nickname = models.CharField(max_length=100, blank=True)

class AlternativePersonName(models.Model):
    person = models.ForeignKey('Person')
    family_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=250, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    
class Family(models.Model):
    family_name = models.CharField(max_length=100)

class Organisation(models.Model):
    name = models.CharField(max_length=250)