# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ItemType'
        db.create_table('eve_itemtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('eve', ['ItemType'])

        # Adding model 'Corporation'
        db.create_table('eve_corporation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('eve', ['Corporation'])

        # Adding model 'Region'
        db.create_table('eve_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal('eve', ['Region'])

        # Adding model 'SolarSystem'
        db.create_table('eve_solarsystem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eve.Region'])),
        ))
        db.send_create_signal('eve', ['SolarSystem'])

        # Adding model 'Station'
        db.create_table('eve_station', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('type_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('solar_system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eve.SolarSystem'], null=True)),
            ('solar_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('corporation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eve.Corporation'], null=True)),
        ))
        db.send_create_signal('eve', ['Station'])


    def backwards(self, orm):
        # Deleting model 'ItemType'
        db.delete_table('eve_itemtype')

        # Deleting model 'Corporation'
        db.delete_table('eve_corporation')

        # Deleting model 'Region'
        db.delete_table('eve_region')

        # Deleting model 'SolarSystem'
        db.delete_table('eve_solarsystem')

        # Deleting model 'Station'
        db.delete_table('eve_station')


    models = {
        'eve.corporation': {
            'Meta': {'object_name': 'Corporation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'eve.itemtype': {
            'Meta': {'object_name': 'ItemType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'eve.region': {
            'Meta': {'object_name': 'Region'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'eve.solarsystem': {
            'Meta': {'object_name': 'SolarSystem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Region']"})
        },
        'eve.station': {
            'Meta': {'object_name': 'Station'},
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Corporation']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'solar_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'solar_system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.SolarSystem']", 'null': 'True'}),
            'type_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['eve']