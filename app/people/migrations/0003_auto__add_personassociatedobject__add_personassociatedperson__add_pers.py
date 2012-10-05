# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PersonAssociatedObject'
        db.create_table('people_personassociatedobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['objects.Object'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.PersonAssociation'])),
        ))
        db.send_create_signal('people', ['PersonAssociatedObject'])

        # Adding model 'PersonAssociatedPerson'
        db.create_table('people_personassociatedperson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('associated_person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='related_person', to=orm['people.Person'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.PersonAssociation'])),
        ))
        db.send_create_signal('people', ['PersonAssociatedPerson'])

        # Adding model 'PersonAssociatedEvent'
        db.create_table('people_personassociatedevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.PersonAssociation'])),
        ))
        db.send_create_signal('people', ['PersonAssociatedEvent'])

        # Adding model 'PersonAssociatedPlace'
        db.create_table('people_personassociatedplace', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['places.Place'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.PersonAssociation'])),
        ))
        db.send_create_signal('people', ['PersonAssociatedPlace'])

        # Adding model 'PersonAddress'
        db.create_table('people_personaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['places.Address'])),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('start_date_month', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('start_date_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('latest_start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('latest_start_date_month', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('latest_start_date_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_date_month', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('end_date_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('earliest_end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('earliest_end_date_month', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('earliest_end_date_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('people', ['PersonAddress'])

        # Adding model 'PersonAssociation'
        db.create_table('people_personassociation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('people', ['PersonAssociation'])

        # Adding M2M table for field rdf_property on 'PersonAssociation'
        db.create_table('people_personassociation_rdf_property', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('personassociation', models.ForeignKey(orm['people.personassociation'], null=False)),
            ('rdfproperty', models.ForeignKey(orm['linkeddata.rdfproperty'], null=False))
        ))
        db.create_unique('people_personassociation_rdf_property', ['personassociation_id', 'rdfproperty_id'])

        # Adding model 'PersonAssociatedOrganisation'
        db.create_table('people_personassociatedorganisation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('organisation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Organisation'])),
            ('association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.PersonAssociation'])),
        ))
        db.send_create_signal('people', ['PersonAssociatedOrganisation'])

        # Adding field 'Person.public'
        db.add_column('people_person', 'public',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Person.mosman_related'
        db.add_column('people_person', 'mosman_related',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Removing M2M table for field roles on 'Person'
        db.delete_table('people_person_roles')

        # Adding field 'Organisation.short_name'
        db.add_column('people_organisation', 'short_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'PersonAssociatedObject'
        db.delete_table('people_personassociatedobject')

        # Deleting model 'PersonAssociatedPerson'
        db.delete_table('people_personassociatedperson')

        # Deleting model 'PersonAssociatedEvent'
        db.delete_table('people_personassociatedevent')

        # Deleting model 'PersonAssociatedPlace'
        db.delete_table('people_personassociatedplace')

        # Deleting model 'PersonAddress'
        db.delete_table('people_personaddress')

        # Deleting model 'PersonAssociation'
        db.delete_table('people_personassociation')

        # Removing M2M table for field rdf_property on 'PersonAssociation'
        db.delete_table('people_personassociation_rdf_property')

        # Deleting model 'PersonAssociatedOrganisation'
        db.delete_table('people_personassociatedorganisation')

        # Deleting field 'Person.public'
        db.delete_column('people_person', 'public')

        # Deleting field 'Person.mosman_related'
        db.delete_column('people_person', 'mosman_related')

        # Adding M2M table for field roles on 'Person'
        db.create_table('people_person_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm['people.person'], null=False)),
            ('personrole', models.ForeignKey(orm['people.personrole'], null=False))
        ))
        db.create_unique('people_person_roles', ['person_id', 'personrole_id'])

        # Deleting field 'Organisation.short_name'
        db.delete_column('people_organisation', 'short_name')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'people.person': {
            'Meta': {'object_name': 'Person'},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['places.Address']", 'null': 'True', 'through': "orm['people.PersonAddress']", 'blank': 'True'}),
            'associated_events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['events.Event']", 'null': 'True', 'through': "orm['people.PersonAssociatedEvent']", 'blank': 'True'}),
            'associated_objects': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['objects.Object']", 'null': 'True', 'through': "orm['people.PersonAssociatedObject']", 'blank': 'True'}),
            'associated_organisations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['people.Organisation']", 'null': 'True', 'through': "orm['people.PersonAssociatedOrganisation']", 'blank': 'True'}),
            'associated_people': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_people'", 'to': "orm['people.Person']", 'through': "orm['people.PersonAssociatedPerson']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'associated_places': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['places.Place']", 'null': 'True', 'through': "orm['people.PersonAssociatedPlace']", 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mosman_related': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'other_names': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'people.personaddress': {
            'Meta': {'object_name': 'PersonAddress'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Address']"}),
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
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
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
        }
    }

    complete_apps = ['people']