# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table('people_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('family_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('other_names', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('people', ['Person'])

        # Adding model 'AlternativePersonName'
        db.create_table('people_alternativepersonname', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('family_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('other_names', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('people', ['AlternativePersonName'])

        # Adding model 'Family'
        db.create_table('people_family', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('family_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('people', ['Family'])

        # Adding model 'Organisation'
        db.create_table('people_organisation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('people', ['Organisation'])


    def backwards(self, orm):
        # Deleting model 'Person'
        db.delete_table('people_person')

        # Deleting model 'AlternativePersonName'
        db.delete_table('people_alternativepersonname')

        # Deleting model 'Family'
        db.delete_table('people_family')

        # Deleting model 'Organisation'
        db.delete_table('people_organisation')


    models = {
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
            'other_names': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['people']