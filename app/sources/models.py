from django.db import models

# Create your models here.

class Source(models.Model):
    title = models.CharField(max_length=250, blank=True, null=True)
    source_type = models.CharField(max_length=50) # include rdf?
    url = models.URLField(blank=True, null=True)
    
    def __unicode__(self):
        return self.title
    