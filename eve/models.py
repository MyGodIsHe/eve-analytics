from django.db import models, transaction
from eve.api import EVEAPI


class ItemType(models.Model):
    name = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)

    def image32(self):
        return 'http://imagetest.eveonline.com/InventoryType/%i_32.png' % self.id

    def image64(self):
        return 'http://imagetest.eveonline.com/InventoryType/%i_64.png' % self.id

    @staticmethod
    @transaction.commit_on_success
    def resolve_all_empty(slice_len):
        """
        http://wiki.eve-id.net/APIv2_Eve_TypeName_XML
        """
        ids = list(ItemType.objects.filter(name='').values_list('id', flat=True))
        ids += list(ItemType.objects.filter(name__isnull=True).values_list('id', flat=True))
        count = len(ids)
        while True:
            slice, ids = ids[:slice_len], ids[slice_len:]
            if not len(slice):
                break
            types = EVEAPI.eve.TypeName(ids=slice).types
            for i in types:
                ItemType.objects.filter(id=i.typeID).update(name=i.typeName)
        return count


class Corporation(models.Model):
    name = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)


class Region(models.Model):
    name = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)

    @staticmethod
    @transaction.commit_on_success
    def resolve_all_empty(slice_len):
        """
        http://wiki.eve-id.net/APIv2_Eve_TypeName_XML
        """
        ids = Region.objects.filter(name__isnull=True).values_list('id', flat=True)
        count = len(ids)
        while True:
            slice, ids = ids[:slice_len], ids[slice_len:]
            if not len(slice):
                break
            characters = EVEAPI.eve.CharacterName(ids=slice).characters
            for i in characters:
                Region.objects.filter(id=i.characterID).update(name=i.name)
        return count


class SolarSystem(models.Model):
    name = models.CharField(max_length=255, null=True)
    region = models.ForeignKey(Region)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)

    @staticmethod
    @transaction.commit_on_success
    def resolve_all_empty(slice_len):
        """
        http://wiki.eve-id.net/APIv2_Eve_TypeName_XML
        """
        ids = SolarSystem.objects.filter(name__isnull=True).values_list('id', flat=True)
        count = len(ids)
        while True:
            slice, ids = ids[:slice_len], ids[slice_len:]
            if not len(slice):
                break
            characters = EVEAPI.eve.CharacterName(ids=slice).characters
            for i in characters:
                SolarSystem.objects.filter(id=i.characterID).update(name=i.name)
        return count


class Station(models.Model):
    name = models.CharField(max_length=255, null=True)
    type_id = models.PositiveIntegerField(null=True)
    solar_system = models.ForeignKey(SolarSystem, null=True)
    solar_id = models.PositiveIntegerField(null=True)
    corporation = models.ForeignKey(Corporation, null=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)

    @staticmethod
    @transaction.commit_on_success
    def resolve_all_empty(slice_len):
        """
        http://wiki.eve-id.net/APIv2_Eve_TypeName_XML
        """
        ids = Station.objects.filter(name__isnull=True).values_list('id', flat=True)
        count = len(ids)
        while True:
            slice, ids = ids[:slice_len], ids[slice_len:]
            if not len(slice):
                break
            characters = EVEAPI.eve.CharacterName(ids=slice).characters
            for i in characters:
                Station.objects.filter(id=i.characterID).update(name=i.name)
        return count

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


class State(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=255)
    value = models.CharField(max_length=255)

    @staticmethod
    def get_value(name, default=''):
        return State.objects.get_or_create(name=name,
            defaults={'name': name, 'value': default}
        )[0].value

    @staticmethod
    def get_int(name, default=0):
        return int(State.get_value(name, default))

    @staticmethod
    def set_value(name, value):
        if not State.objects.filter(name=name).update(value=str(value)):
            State(name=name, value=value).save()


class SkipChart(models.Model):
    queue_size = models.IntegerField()
    package_percent = models.FloatField()
    row_percent = models.FloatField()
    create_at = models.DateTimeField(auto_now_add=True)