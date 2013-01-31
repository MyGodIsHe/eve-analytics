# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        for i in orm['eve.SkipChart'].objects.all():
            orm['eve.SkipChart'].objects.filter(id=i.id).update(percent=i.value)

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'eve.corporation': {
            'Meta': {'ordering': "['name']", 'object_name': 'Corporation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'eve.itemtype': {
            'Meta': {'ordering': "['name']", 'object_name': 'ItemType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'eve.order': {
            'Meta': {'object_name': 'Order'},
            'bid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.ItemType']"}),
            'min_volume': ('django.db.models.fields.IntegerField', [], {}),
            'range': ('django.db.models.fields.IntegerField', [], {}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Region']"}),
            'solar_system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.SolarSystem']"}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Station']"}),
            'vol_entered': ('django.db.models.fields.IntegerField', [], {})
        },
        'eve.orderchange': {
            'Meta': {'unique_together': "(('order', 'price', 'vol_remaining', 'issue_date'),)", 'object_name': 'OrderChange'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_date': ('django.db.models.fields.DateTimeField', [], {}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Order']"}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'vol_remaining': ('django.db.models.fields.IntegerField', [], {})
        },
        'eve.region': {
            'Meta': {'ordering': "['name']", 'object_name': 'Region'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'eve.skipchart': {
            'Meta': {'object_name': 'SkipChart'},
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'eve.solarsystem': {
            'Meta': {'ordering': "['name']", 'object_name': 'SolarSystem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Region']"})
        },
        'eve.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'eve.station': {
            'Meta': {'ordering': "['name']", 'object_name': 'Station'},
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Corporation']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'solar_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'solar_system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.SolarSystem']", 'null': 'True'}),
            'type_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['eve']
    symmetrical = True
