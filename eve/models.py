from django.db import models, transaction
from eve.api import EVEAPI
from utils import rel


class ItemType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return unicode(self.name)

    def image32(self):
        return 'http://imagetest.eveonline.com/InventoryType/%i_32.png' % self.id

    def image64(self):
        return 'http://imagetest.eveonline.com/InventoryType/%i_64.png' % self.id

    def name_by_id(self):
        return EVEAPI.eve.CharacterName(ids=self.id).characters[0].name

    @staticmethod
    @transaction.commit_on_success
    def update_from_eve():
        with file(rel('raw/typeids.txt')) as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    id, name = line.split(None, 1)
                    ItemType(pk=int(id), name=name).save()


class Corporation(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return unicode(self.name)


class Region(models.Model):
    name = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return unicode(self.name)

    def name_by_id(self):
        return EVEAPI.eve.CharacterName(ids=self.id).characters[0].name


class SolarSystem(models.Model):
    name = models.CharField(max_length=255, null=True)
    region = models.ForeignKey(Region)

    def __unicode__(self):
        return unicode(self.name)

    def name_by_id(self):
        return EVEAPI.eve.CharacterName(ids=self.id).characters[0].name


class Station(models.Model):
    name = models.CharField(max_length=255, null=True)
    type_id = models.PositiveIntegerField(null=True)
    solar_system = models.ForeignKey(SolarSystem, null=True)
    solar_id = models.PositiveIntegerField(null=True)
    corporation = models.ForeignKey(Corporation, null=True)

    def __unicode__(self):
        return unicode(self.name)

    @staticmethod
    @transaction.commit_on_success
    def update_from_eve():
        for i in EVEAPI.eve.ConquerableStationList().outposts:
            corp, is_create = Corporation.objects.get_or_create(
                id=i.corporationID,
                defaults={'name': i.corporationName})
            Station(
                id=i.stationID,
                name=i.stationName,
                type_id=i.stationTypeID,
                solar_id=i.solarSystemID,
                corporation=corp,
            ).save()


class Order(models.Model):
    item_type = models.ForeignKey(ItemType)
    bid = models.BooleanField()

    range = models.IntegerField()
    duration = models.IntegerField()
    vol_entered = models.IntegerField()
    min_volume = models.IntegerField()

    region = models.ForeignKey(Region)
    station = models.ForeignKey(Station)
    solar_system = models.ForeignKey(SolarSystem)

    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True)

    def __unicode__(self):
        return unicode(self.id)


class OrderChange(models.Model):
    order = models.ForeignKey(Order)
    price = models.FloatField()
    vol_remaining = models.IntegerField()
    issue_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', 'price', 'vol_remaining', 'issue_date')

    def __unicode__(self):
        return unicode(self.id)


class Stat(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=255)
    value = models.CharField(max_length=255)



    @staticmethod
    def get_value(name, default=''):
        return Stat.objects.get_or_create(name=name,
            defaults={'name': name, 'value': default}
        )[0].value

    @staticmethod
    def get_int(name, default=0):
        return int(Stat.get_value(name, default))

    @staticmethod
    def set_value(name, value):
        if not Stat.objects.filter(name=name).update(value=str(value)):
            Stat(name=name, value=value).save()