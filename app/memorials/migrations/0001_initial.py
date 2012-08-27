# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Memorial'
        db.create_table('memorials_memorial', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='memorial_location', null=True, to=orm['places.Place'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('inscription', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('memorials', ['Memorial'])

        # Adding model 'MemorialPart'
        db.create_table('memorials_memorialpart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.Memorial'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('inscription', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('memorials', ['MemorialPart'])

        # Adding model 'MemorialImage'
        db.create_table('memorials_memorialimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.Memorial'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('memorials', ['MemorialImage'])

        # Adding model 'MemorialName'
        db.create_table('memorials_memorialname', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.Memorial'])),
            ('memorial_part', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.MemorialPart'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('inscription', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('row', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('column', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'], null=True, blank=True)),
        ))
        db.send_create_signal('memorials', ['MemorialName'])

        # Adding model 'MemorialAssociatedPerson'
        db.create_table('memorials_memorialassociatedperson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.Memorial'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.MemorialAssociation'])),
        ))
        db.send_create_signal('memorials', ['MemorialAssociatedPerson'])

        # Adding model 'MemorialAssociatedOrganisation'
        db.create_table('memorials_memorialassociatedorganisation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.Memorial'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Organisation'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.MemorialAssociation'])),
        ))
        db.send_create_signal('memorials', ['MemorialAssociatedOrganisation'])

        # Adding model 'MemorialAssociatedEvent'
        db.create_table('memorials_memorialassociatedevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.Memorial'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.MemorialAssociation'])),
        ))
        db.send_create_signal('memorials', ['MemorialAssociatedEvent'])

        # Adding model 'MemorialAssociatedPlace'
        db.create_table('memorials_memorialassociatedplace', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.Memorial'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['places.Place'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.MemorialAssociation'])),
        ))
        db.send_create_signal('memorials', ['MemorialAssociatedPlace'])

        # Adding model 'MemorialAssociatedObject'
        db.create_table('memorials_memorialassociatedobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.Memorial'])),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['objects.Object'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.MemorialAssociation'])),
        ))
        db.send_create_signal('memorials', ['MemorialAssociatedObject'])

        # Adding model 'MemorialAssociatedSource'
        db.create_table('memorials_memorialassociatedsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memorial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.Memorial'])),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sources.Source'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memorials.MemorialAssociation'])),
        ))
        db.send_create_signal('memorials', ['MemorialAssociatedSource'])

        # Adding model 'MemorialAssociation'
        db.create_table('memorials_memorialassociation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('association', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('rdf_property', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
        ))
        db.send_create_signal('memorials', ['MemorialAssociation'])


    def backwards(self, orm):
        # Deleting model 'Memorial'
        db.delete_table('memorials_memorial')

        # Deleting model 'MemorialPart'
        db.delete_table('memorials_memorialpart')

        # Deleting model 'MemorialImage'
        db.delete_table('memorials_memorialimage')

        # Deleting model 'MemorialName'
        db.delete_table('memorials_memorialname')

        # Deleting model 'MemorialAssociatedPerson'
        db.delete_table('memorials_memorialassociatedperson')

        # Deleting model 'MemorialAssociatedOrganisation'
        db.delete_table('memorials_memorialassociatedorganisation')

        # Deleting model 'MemorialAssociatedEvent'
        db.delete_table('memorials_memorialassociatedevent')

        # Deleting model 'MemorialAssociatedPlace'
        db.delete_table('memorials_memorialassociatedplace')

        # Deleting model 'MemorialAssociatedObject'
        db.delete_table('memorials_memorialassociatedobject')

        # Deleting model 'MemorialAssociatedSource'
        db.delete_table('memorials_memorialassociatedsource')

        # Deleting model 'MemorialAssociation'
        db.delete_table('memorials_memorialassociation')


    models = {
        'events.event': {
            'Meta': {'object_name': 'Event'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        },
        'memorials.memorial': {
            'Meta': {'object_name': 'Memorial'},
            'associated_events': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['events.Event']", 'through': "orm['memorials.MemorialAssociatedEvent']", 'symmetrical': 'False'}),
            'associated_objects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['objects.Object']", 'through': "orm['memorials.MemorialAssociatedObject']", 'symmetrical': 'False'}),
            'associated_organisations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Organisation']", 'through': "orm['memorials.MemorialAssociatedOrganisation']", 'symmetrical': 'False'}),
            'associated_people': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Person']", 'through': "orm['memorials.MemorialAssociatedPerson']", 'symmetrical': 'False'}),
            'associated_places': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['places.Place']", 'through': "orm['memorials.MemorialAssociatedPlace']", 'symmetrical': 'False'}),
            'associated_sources': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sources.Source']", 'through': "orm['memorials.MemorialAssociatedSource']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscription': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'memorial_location'", 'null': 'True', 'to': "orm['places.Place']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        'memorials.memorialassociatedevent': {
            'Meta': {'object_name': 'MemorialAssociatedEvent'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.MemorialAssociation']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.Memorial']"})
        },
        'memorials.memorialassociatedobject': {
            'Meta': {'object_name': 'MemorialAssociatedObject'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.MemorialAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.Memorial']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['objects.Object']"})
        },
        'memorials.memorialassociatedorganisation': {
            'Meta': {'object_name': 'MemorialAssociatedOrganisation'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.MemorialAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.Memorial']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Organisation']"})
        },
        'memorials.memorialassociatedperson': {
            'Meta': {'object_name': 'MemorialAssociatedPerson'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.MemorialAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.Memorial']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"})
        },
        'memorials.memorialassociatedplace': {
            'Meta': {'object_name': 'MemorialAssociatedPlace'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.MemorialAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.Memorial']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Place']"})
        },
        'memorials.memorialassociatedsource': {
            'Meta': {'object_name': 'MemorialAssociatedSource'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.MemorialAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.Memorial']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.Source']"})
        },
        'memorials.memorialassociation': {
            'Meta': {'object_name': 'MemorialAssociation'},
            'association': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rdf_property': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        'memorials.memorialimage': {
            'Meta': {'object_name': 'MemorialImage'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'memorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.Memorial']"})
        },
        'memorials.memorialname': {
            'Meta': {'object_name': 'MemorialName'},
            'column': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscription': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'memorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.Memorial']"}),
            'memorial_part': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.MemorialPart']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']", 'null': 'True', 'blank': 'True'}),
            'row': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'memorials.memorialpart': {
            'Meta': {'object_name': 'MemorialPart'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscription': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'memorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['memorials.Memorial']"})
        },
        'objects.object': {
            'Meta': {'object_name': 'Object'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
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
        },
        'places.place': {
            'Meta': {'object_name': 'Place'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        'sources.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['memorials']