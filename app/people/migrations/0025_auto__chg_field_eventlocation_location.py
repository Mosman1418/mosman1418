# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'EventLocation.location'
        db.alter_column('people_eventlocation', 'location_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['places.Place'], null=True))

    def backwards(self, orm):

        # Changing field 'EventLocation.location'
        db.alter_column('people_eventlocation', 'location_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['places.Place']))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'other_names': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sources.Source']", 'null': 'True', 'blank': 'True'})
        },
        'people.birth': {
            'Meta': {'object_name': 'Birth'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Place']", 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sources.Source']", 'null': 'True', 'blank': 'True'}),
            'start_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'people.death': {
            'Meta': {'object_name': 'Death'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Place']", 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sources.Source']", 'null': 'True', 'blank': 'True'}),
            'start_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'people.eventlocation': {
            'Meta': {'object_name': 'EventLocation'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.EventLocationAssociation']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lifeevent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.LifeEvent']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Place']", 'null': 'True', 'blank': 'True'})
        },
        'people.eventlocationassociation': {
            'Meta': {'object_name': 'EventLocationAssociation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rdf_property': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['linkeddata.RDFProperty']", 'null': 'True', 'blank': 'True'})
        },
        'people.family': {
            'Meta': {'object_name': 'Family'},
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'people.lifeevent': {
            'Meta': {'object_name': 'LifeEvent'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.LifeEventType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['places.Place']", 'null': 'True', 'through': "orm['people.EventLocation']", 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sources.Source']", 'null': 'True', 'blank': 'True'}),
            'start_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'people.lifeeventtype': {
            'Meta': {'object_name': 'LifeEventType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rdf_class': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['linkeddata.RDFClass']", 'null': 'True', 'blank': 'True'})
        },
        'people.lifeperiod': {
            'Meta': {'object_name': 'LifePeriod'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'start_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'people.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'associated_sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sources.Source']", 'null': 'True', 'through': "orm['people.OrganisationAssociatedSource']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['people.PeopleImage']", 'null': 'True', 'blank': 'True'}),
            'mosman_related': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'stories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['people.PeopleStory']", 'null': 'True', 'blank': 'True'})
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
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'caption': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'people.peoplestory': {
            'Meta': {'object_name': 'PeopleStory'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'people.person': {
            'Meta': {'ordering': "['family_name', 'other_names']", 'object_name': 'Person'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['places.Address']", 'null': 'True', 'through': "orm['people.PersonAddress']", 'blank': 'True'}),
            'associated_events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['events.Event']", 'null': 'True', 'through': "orm['people.PersonAssociatedEvent']", 'blank': 'True'}),
            'associated_objects': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['objects.Object']", 'null': 'True', 'through': "orm['people.PersonAssociatedObject']", 'blank': 'True'}),
            'associated_organisations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['people.Organisation']", 'null': 'True', 'through': "orm['people.PersonAssociatedOrganisation']", 'blank': 'True'}),
            'associated_people': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_people'", 'to': "orm['people.Person']", 'through': "orm['people.PersonAssociatedPerson']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'associated_places': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['places.Place']", 'null': 'True', 'through': "orm['people.PersonAssociatedPlace']", 'blank': 'True'}),
            'associated_sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sources.Source']", 'null': 'True', 'through': "orm['people.PersonAssociatedSource']", 'blank': 'True'}),
            'biography': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'birth_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'birth_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birth_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birth_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'birth_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birth_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'death_earliest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'death_earliest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'death_earliest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'death_latest_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'death_latest_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'death_latest_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.Source']"})
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
        'people.repository': {
            'Meta': {'object_name': 'Repository'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'daa_id': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'places.address': {
            'Meta': {'object_name': 'Address'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'street_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'street_number': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        'places.place': {
            'Meta': {'object_name': 'Place'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'geonames_id': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'place_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'sources.source': {
            'Meta': {'object_name': 'Source'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'citation': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collection_source'", 'null': 'True', 'to': "orm['sources.Source']"}),
            'collection_item_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'collection_title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'creators': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['people.Person']", 'null': 'True', 'through': "orm['sources.SourcePerson']", 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'pages': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'publication_date_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publication_date_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'publication_date_end_day_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publication_date_end_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publication_date_month_known': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publication_place': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rdf_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Repository']", 'null': 'True', 'blank': 'True'}),
            'repository_item_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.SourceType']"}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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