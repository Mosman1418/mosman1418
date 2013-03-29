# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'RDFProperty.inverse'
        db.delete_column('linkeddata_rdfproperty', 'inverse')

        # Adding field 'RDFProperty.inverse_rdf_property'
        db.add_column('linkeddata_rdfproperty', 'inverse_rdf_property',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'RDFProperty.inverse'
        db.add_column('linkeddata_rdfproperty', 'inverse',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'RDFProperty.inverse_rdf_property'
        db.delete_column('linkeddata_rdfproperty', 'inverse_rdf_property')


    models = {
        'linkeddata.rdfclass': {
            'Meta': {'object_name': 'RDFClass'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rdf_class': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['linkeddata.RDFSchema']"})
        },
        'linkeddata.rdfproperty': {
            'Meta': {'object_name': 'RDFProperty'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inverse_rdf_property': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'rdf_property': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['linkeddata.RDFSchema']"})
        },
        'linkeddata.rdfschema': {
            'Meta': {'object_name': 'RDFSchema'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['linkeddata']