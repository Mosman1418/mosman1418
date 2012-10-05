# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PersonRole'
        db.create_table('people_personrole', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('people', ['PersonRole'])

        # Adding M2M table for field rdf_property on 'PersonRole'
        db.create_table('people_personrole_rdf_property', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('personrole', models.ForeignKey(orm['people.personrole'], null=False)),
            ('rdfproperty', models.ForeignKey(orm['linkeddata.rdfproperty'], null=False))
        ))
        db.create_unique('people_personrole_rdf_property', ['personrole_id', 'rdfproperty_id'])

        # Adding M2M table for field roles on 'Person'
        db.create_table('people_person_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm['people.person'], null=False)),
            ('personrole', models.ForeignKey(orm['people.personrole'], null=False))
        ))
        db.create_unique('people_person_roles', ['person_id', 'personrole_id'])


    def backwards(self, orm):
        # Deleting model 'PersonRole'
        db.delete_table('people_personrole')

        # Removing M2M table for field rdf_property on 'PersonRole'
        db.delete_table('people_personrole_rdf_property')

        # Removing M2M table for field roles on 'Person'
        db.delete_table('people_person_roles')


    models = {
        'linkeddata.rdfproperty': {
            'Meta': {'object_name': 'RDFProperty'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inverse': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'rdf_property': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['linkeddata.RDFSchema']"})
        },
        'linkeddata.rdfschema': {
            'Meta': {'object_name': 'RDFSchema'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'people.alternativepersonname': {
            'Meta': {'object_name': 'AlternativePersonName'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'other_names': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"})
        },
        'people.family': {
            'Meta': {'object_name': 'Family'},
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'people.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'people.person': {
            'Meta': {'object_name': 'Person'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'other_names': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.PersonRole']", 'symmetrical': 'False'})
        },
        'people.personrole': {
            'Meta': {'object_name': 'PersonRole'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rdf_property': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['linkeddata.RDFProperty']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['people']