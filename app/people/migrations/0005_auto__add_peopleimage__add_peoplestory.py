# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PeopleImage'
        db.create_table('people_peopleimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('caption', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('people', ['PeopleImage'])

        # Adding model 'PeopleStory'
        db.create_table('people_peoplestory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('people', ['PeopleStory'])

        # Adding M2M table for field images on 'Person'
        db.create_table('people_person_images', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm['people.person'], null=False)),
            ('peopleimage', models.ForeignKey(orm['people.peopleimage'], null=False))
        ))
        db.create_unique('people_person_images', ['person_id', 'peopleimage_id'])

        # Adding M2M table for field stories on 'Person'
        db.create_table('people_person_stories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm['people.person'], null=False)),
            ('peoplestory', models.ForeignKey(orm['people.peoplestory'], null=False))
        ))
        db.create_unique('people_person_stories', ['person_id', 'peoplestory_id'])


    def backwards(self, orm):
        # Deleting model 'PeopleImage'
        db.delete_table('people_peopleimage')

        # Deleting model 'PeopleStory'
        db.delete_table('people_peoplestory')

        # Removing M2M table for field images on 'Person'
        db.delete_table('people_person_images')

        # Removing M2M table for field stories on 'Person'
        db.delete_table('people_person_stories')


    models = {
        'events.event': {
            'Meta': {'object_name': 'Event'},
            'date_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'earliest_end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'earliest_end_date_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'earliest_end_date_month': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_date_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date_month': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'latest_start_date_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latest_start_date_month': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_date_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_date_month': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        },
        'linkeddata.rdfclass': {
            'Meta': {'object_name': 'RDFClass'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rdf_class': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['linkeddata.RDFSchema']"})
        },
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
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'objects.object': {
            'Meta': {'object_name': 'Object'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
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
            'associated_sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sources.Source']", 'null': 'True', 'through': "orm['people.OrganisationAssociatedSource']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mosman_related': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'people.organisationassociatedsource': {
            'Meta': {'object_name': 'OrganisationAssociatedSource'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.PersonAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Organisation']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.Source']"})
        },
        'people.peopleimage': {
            'Meta': {'object_name': 'PeopleImage'},
            'caption': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'people.peoplestory': {
            'Meta': {'object_name': 'PeopleStory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'people.person': {
            'Meta': {'object_name': 'Person'},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['places.Address']", 'null': 'True', 'through': "orm['people.PersonAddress']", 'blank': 'True'}),
            'associated_events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['events.Event']", 'null': 'True', 'through': "orm['people.PersonAssociatedEvent']", 'blank': 'True'}),
            'associated_objects': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['objects.Object']", 'null': 'True', 'through': "orm['people.PersonAssociatedObject']", 'blank': 'True'}),
            'associated_organisations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['people.Organisation']", 'null': 'True', 'through': "orm['people.PersonAssociatedOrganisation']", 'blank': 'True'}),
            'associated_people': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_people'", 'to': "orm['people.Person']", 'through': "orm['people.PersonAssociatedPerson']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'associated_places': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['places.Place']", 'null': 'True', 'through': "orm['people.PersonAssociatedPlace']", 'blank': 'True'}),
            'associated_sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sources.Source']", 'null': 'True', 'through': "orm['people.PersonAssociatedSource']", 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['people.PeopleImage']", 'null': 'True', 'blank': 'True'}),
            'mosman_related': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'other_names': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'stories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['people.PeopleStory']", 'null': 'True', 'blank': 'True'})
        },
        'people.personaddress': {
            'Meta': {'object_name': 'PersonAddress'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Address']"}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_date_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date_month': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sources.Source']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_date_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_date_month': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'people.personassociatedevent': {
            'Meta': {'object_name': 'PersonAssociatedEvent'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.PersonAssociation']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"})
        },
        'people.personassociatedobject': {
            'Meta': {'object_name': 'PersonAssociatedObject'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.PersonAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['objects.Object']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"})
        },
        'people.personassociatedorganisation': {
            'Meta': {'object_name': 'PersonAssociatedOrganisation'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.PersonAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Organisation']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"})
        },
        'people.personassociatedperson': {
            'Meta': {'object_name': 'PersonAssociatedPerson'},
            'associated_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_person'", 'to': "orm['people.Person']"}),
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.PersonAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"})
        },
        'people.personassociatedplace': {
            'Meta': {'object_name': 'PersonAssociatedPlace'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.PersonAssociation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Place']"})
        },
        'people.personassociatedsource': {
            'Meta': {'object_name': 'PersonAssociatedSource'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.PersonAssociation']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.Source']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"})
        },
        'people.personassociation': {
            'Meta': {'object_name': 'PersonAssociation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rdf_property': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['linkeddata.RDFProperty']", 'null': 'True', 'blank': 'True'})
        },
        'people.personrole': {
            'Meta': {'object_name': 'PersonRole'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rdf_property': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['linkeddata.RDFProperty']", 'null': 'True', 'blank': 'True'})
        },
        'places.address': {
            'Meta': {'object_name': 'Address'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'street_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'street_number': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
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
            'citation': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collection_source'", 'null': 'True', 'to': "orm['sources.Source']"}),
            'collection_item_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'collection_title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'creators': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['people.Person']", 'null': 'True', 'through': "orm['sources.SourcePerson']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'pages': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'publication_date_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publication_date_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'publication_date_end_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publication_date_end_month': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publication_date_month': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publication_place': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'publisher_source'", 'null': 'True', 'to': "orm['people.Organisation']"}),
            'rdf_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'repository_source'", 'null': 'True', 'to': "orm['people.Organisation']"}),
            'repository_item_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.SourceType']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'sources.sourceperson': {
            'Meta': {'object_name': 'SourcePerson'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.SourceRole']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.Source']"})
        },
        'sources.sourcerole': {
            'Meta': {'object_name': 'SourceRole'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rdf_property': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['linkeddata.RDFProperty']", 'null': 'True', 'blank': 'True'})
        },
        'sources.sourcetype': {
            'Meta': {'object_name': 'SourceType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rdf_class': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['linkeddata.RDFClass']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['people']