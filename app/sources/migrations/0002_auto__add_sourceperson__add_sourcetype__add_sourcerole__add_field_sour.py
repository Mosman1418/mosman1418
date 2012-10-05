# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SourcePerson'
        db.create_table('sources_sourceperson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sources.Source'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sources.SourceRole'])),
        ))
        db.send_create_signal('sources', ['SourcePerson'])

        # Adding model 'SourceType'
        db.create_table('sources_sourcetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('sources', ['SourceType'])

        # Adding M2M table for field rdf_class on 'SourceType'
        db.create_table('sources_sourcetype_rdf_class', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sourcetype', models.ForeignKey(orm['sources.sourcetype'], null=False)),
            ('rdfclass', models.ForeignKey(orm['linkeddata.rdfclass'], null=False))
        ))
        db.create_unique('sources_sourcetype_rdf_class', ['sourcetype_id', 'rdfclass_id'])

        # Adding model 'SourceRole'
        db.create_table('sources_sourcerole', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('sources', ['SourceRole'])

        # Adding M2M table for field rdf_property on 'SourceRole'
        db.create_table('sources_sourcerole_rdf_property', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sourcerole', models.ForeignKey(orm['sources.sourcerole'], null=False)),
            ('rdfproperty', models.ForeignKey(orm['linkeddata.rdfproperty'], null=False))
        ))
        db.create_unique('sources_sourcerole_rdf_property', ['sourcerole_id', 'rdfproperty_id'])

        # Adding field 'Source.publisher'
        db.add_column('sources_source', 'publisher',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='publisher_source', null=True, to=orm['people.Organisation']),
                      keep_default=False)

        # Adding field 'Source.publication_place'
        db.add_column('sources_source', 'publication_place',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Source.publication_date'
        db.add_column('sources_source', 'publication_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Source.publication_date_month'
        db.add_column('sources_source', 'publication_date_month',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Source.publication_date_day'
        db.add_column('sources_source', 'publication_date_day',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Source.collection'
        db.add_column('sources_source', 'collection',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='collection_source', null=True, to=orm['sources.Source']),
                      keep_default=False)

        # Adding field 'Source.collection_title'
        db.add_column('sources_source', 'collection_title',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Source.collection_item_id'
        db.add_column('sources_source', 'collection_item_id',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Source.repository_item_id'
        db.add_column('sources_source', 'repository_item_id',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Source.repository'
        db.add_column('sources_source', 'repository',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='repository_source', null=True, to=orm['people.Organisation']),
                      keep_default=False)

        # Adding field 'Source.citation'
        db.add_column('sources_source', 'citation',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Source.pages'
        db.add_column('sources_source', 'pages',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Source.rdf_url'
        db.add_column('sources_source', 'rdf_url',
                      self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Source.json_url'
        db.add_column('sources_source', 'json_url',
                      self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True),
                      keep_default=False)


        # Renaming column for 'Source.source_type' to match new field type.
        db.rename_column('sources_source', 'source_type', 'source_type_id')
        # Changing field 'Source.source_type'
        db.alter_column('sources_source', 'source_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sources.SourceType']))
        # Adding index on 'Source', fields ['source_type']
        db.create_index('sources_source', ['source_type_id'])


    def backwards(self, orm):
        # Removing index on 'Source', fields ['source_type']
        db.delete_index('sources_source', ['source_type_id'])

        # Deleting model 'SourcePerson'
        db.delete_table('sources_sourceperson')

        # Deleting model 'SourceType'
        db.delete_table('sources_sourcetype')

        # Removing M2M table for field rdf_class on 'SourceType'
        db.delete_table('sources_sourcetype_rdf_class')

        # Deleting model 'SourceRole'
        db.delete_table('sources_sourcerole')

        # Removing M2M table for field rdf_property on 'SourceRole'
        db.delete_table('sources_sourcerole_rdf_property')

        # Deleting field 'Source.publisher'
        db.delete_column('sources_source', 'publisher_id')

        # Deleting field 'Source.publication_place'
        db.delete_column('sources_source', 'publication_place')

        # Deleting field 'Source.publication_date'
        db.delete_column('sources_source', 'publication_date')

        # Deleting field 'Source.publication_date_month'
        db.delete_column('sources_source', 'publication_date_month')

        # Deleting field 'Source.publication_date_day'
        db.delete_column('sources_source', 'publication_date_day')

        # Deleting field 'Source.collection'
        db.delete_column('sources_source', 'collection_id')

        # Deleting field 'Source.collection_title'
        db.delete_column('sources_source', 'collection_title')

        # Deleting field 'Source.collection_item_id'
        db.delete_column('sources_source', 'collection_item_id')

        # Deleting field 'Source.repository_item_id'
        db.delete_column('sources_source', 'repository_item_id')

        # Deleting field 'Source.repository'
        db.delete_column('sources_source', 'repository_id')

        # Deleting field 'Source.citation'
        db.delete_column('sources_source', 'citation')

        # Deleting field 'Source.pages'
        db.delete_column('sources_source', 'pages')

        # Deleting field 'Source.rdf_url'
        db.delete_column('sources_source', 'rdf_url')

        # Deleting field 'Source.json_url'
        db.delete_column('sources_source', 'json_url')


        # Renaming column for 'Source.source_type' to match new field type.
        db.rename_column('sources_source', 'source_type_id', 'source_type')
        # Changing field 'Source.source_type'
        db.alter_column('sources_source', 'source_type', self.gf('django.db.models.fields.CharField')(max_length=50))

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

    complete_apps = ['sources']