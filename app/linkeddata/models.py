from django.db import models

# Create your models here.


class RDFSchema(models.Model):
    prefix = models.CharField(max_length=20)
    uri = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s: %s' % (self.prefix, self.uri)


class RDFProperty(models.Model):
    schema = models.ForeignKey('RDFSchema')
    rdf_property = models.CharField(max_length=50)
    inverse = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return '%s: %s' % (self.schema.prefix, self.rdf_property)


class RDFClass(models.Model):
    schema = models.ForeignKey('RDFSchema')
    rdf_class = models.CharField(max_length=50)

    def __unicode__(self):
        return '%s: %s' % (self.schema.prefix, self.rdf_class)

