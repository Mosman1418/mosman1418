# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Event.description'
        db.add_column('events_event', 'description',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.date_type'
        db.add_column('events_event', 'date_type',
                      self.gf('django.db.models.fields.CharField')(default='instance', max_length=10),
                      keep_default=False)

        # Adding field 'Event.start_date'
        db.add_column('events_event', 'start_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.start_date_month'
        db.add_column('events_event', 'start_date_month',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Event.start_date_day'
        db.add_column('events_event', 'start_date_day',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Event.latest_start_date'
        db.add_column('events_event', 'latest_start_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.latest_start_date_month'
        db.add_column('events_event', 'latest_start_date_month',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Event.latest_start_date_day'
        db.add_column('events_event', 'latest_start_date_day',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Event.end_date'
        db.add_column('events_event', 'end_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.end_date_month'
        db.add_column('events_event', 'end_date_month',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Event.end_date_day'
        db.add_column('events_event', 'end_date_day',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Event.earliest_end_date'
        db.add_column('events_event', 'earliest_end_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.earliest_end_date_month'
        db.add_column('events_event', 'earliest_end_date_month',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Event.earliest_end_date_day'
        db.add_column('events_event', 'earliest_end_date_day',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Event.description'
        db.delete_column('events_event', 'description')

        # Deleting field 'Event.date_type'
        db.delete_column('events_event', 'date_type')

        # Deleting field 'Event.start_date'
        db.delete_column('events_event', 'start_date')

        # Deleting field 'Event.start_date_month'
        db.delete_column('events_event', 'start_date_month')

        # Deleting field 'Event.start_date_day'
        db.delete_column('events_event', 'start_date_day')

        # Deleting field 'Event.latest_start_date'
        db.delete_column('events_event', 'latest_start_date')

        # Deleting field 'Event.latest_start_date_month'
        db.delete_column('events_event', 'latest_start_date_month')

        # Deleting field 'Event.latest_start_date_day'
        db.delete_column('events_event', 'latest_start_date_day')

        # Deleting field 'Event.end_date'
        db.delete_column('events_event', 'end_date')

        # Deleting field 'Event.end_date_month'
        db.delete_column('events_event', 'end_date_month')

        # Deleting field 'Event.end_date_day'
        db.delete_column('events_event', 'end_date_day')

        # Deleting field 'Event.earliest_end_date'
        db.delete_column('events_event', 'earliest_end_date')

        # Deleting field 'Event.earliest_end_date_month'
        db.delete_column('events_event', 'earliest_end_date_month')

        # Deleting field 'Event.earliest_end_date_day'
        db.delete_column('events_event', 'earliest_end_date_day')


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
        }
    }

    complete_apps = ['events']