from django.db import models

# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=250, blank=True, null=True)