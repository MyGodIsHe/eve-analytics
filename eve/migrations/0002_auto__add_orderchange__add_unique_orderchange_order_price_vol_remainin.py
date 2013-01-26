# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.execute('''
BEGIN;
CREATE TABLE `eve_order` (
    `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `item_type_id` integer NOT NULL,
    `bid` bool NOT NULL,
    `range` integer NOT NULL,
    `duration` integer NOT NULL,
    `vol_entered` integer NOT NULL,
    `min_volume` integer NOT NULL,
    `region_id` integer NOT NULL,
    `station_id` integer NOT NULL,
    `solar_system_id` integer NOT NULL,
    `created_at` datetime NOT NULL,
    `closed_at` datetime
)
;
ALTER TABLE `eve_order` ADD CONSTRAINT `region_id_refs_id_ee8fd460` FOREIGN KEY (`region_id`) REFERENCES `eve_region` (`id`);
ALTER TABLE `eve_order` ADD CONSTRAINT `station_id_refs_id_8c776ffd` FOREIGN KEY (`station_id`) REFERENCES `eve_station` (`id`);
ALTER TABLE `eve_order` ADD CONSTRAINT `item_type_id_refs_id_bff47cc5` FOREIGN KEY (`item_type_id`) REFERENCES `eve_itemtype` (`id`);
ALTER TABLE `eve_order` ADD CONSTRAINT `solar_system_id_refs_id_94842813` FOREIGN KEY (`solar_system_id`) REFERENCES `eve_solarsystem` (`id`);
CREATE TABLE `eve_orderchange` (
    `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `order_id` bigint NOT NULL,
    `price` double precision NOT NULL,
    `vol_remaining` integer NOT NULL,
    `issue_date` datetime NOT NULL,
    `created_at` datetime NOT NULL,
    UNIQUE (`order_id`, `price`, `vol_remaining`, `issue_date`)
)
;
ALTER TABLE `eve_orderchange` ADD CONSTRAINT `order_id_refs_id_687803a9` FOREIGN KEY (`order_id`) REFERENCES `eve_order` (`id`);
CREATE INDEX `eve_order_38d6fbe9` ON `eve_order` (`item_type_id`);
CREATE INDEX `eve_order_f6a8b032` ON `eve_order` (`region_id`);
CREATE INDEX `eve_order_15e3331d` ON `eve_order` (`station_id`);
CREATE INDEX `eve_order_ed89f5d1` ON `eve_order` (`solar_system_id`);
CREATE INDEX `eve_orderchange_8337030b` ON `eve_orderchange` (`order_id`);
COMMIT;
        ''')


    def backwards(self, orm):
        # Removing unique constraint on 'OrderChange', fields ['order', 'price', 'vol_remaining', 'issue_date']
        db.delete_unique('eve_orderchange', ['order_id', 'price', 'vol_remaining', 'issue_date'])

        # Deleting model 'OrderChange'
        db.delete_table('eve_orderchange')

        # Deleting model 'Order'
        db.delete_table('eve_order')


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