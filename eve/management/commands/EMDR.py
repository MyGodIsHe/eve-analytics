"""
API: https://eve-market-data-relay.readthedocs.org/en/latest/
Data Format: http://dev.eve-central.com/unifieduploader/start
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import zlib
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime
from eve.models import Order, OrderChange, ItemType, Region, Station, SolarSystem

import zmq.green as zmq
from django.utils import simplejson
from django_rq import job


@job
def processing(market_data):
    region_id = None
    for rowset in market_data['rowsets']:
        if rowset['regionID']:
            region_id = rowset['regionID']
            break
    if not region_id:
        return

    region = Region.objects.get_or_create(id=region_id)[0]

    for rowset in market_data['rowsets']:
        orders = []

        for row in rowset['rows']:
            row = dict(zip(market_data['columns'], row))

            issue_date = parse_datetime(row['issueDate'])

            if not Order.objects.filter(id=row['orderID']).count():
                order = Order(
                    id=row['orderID'],
                    bid=row['bid'],
                    range=row['range'],
                    duration=row['duration'],
                    vol_entered=row['volEntered'],
                    min_volume=row['minVolume'],
                    region=region,
                )
                order.item_type = ItemType.objects.get_or_create(id=rowset['typeID'])[0]
                order.station = Station.objects.get_or_create(id=row['stationID'])[0]
                if row['solarSystemID']:
                    order.solar_system = SolarSystem.objects.get_or_create(
                        id=row['solarSystemID'], defaults={'region_id':region_id})[0]
                order.save()

            try:
                OrderChange(
                    order_id=row['orderID'],
                    price=row['price'],
                    vol_remaining=row['volRemaining'],
                    issue_date=issue_date,
                ).save()
            except IntegrityError as e:
                if e.args != 1062:
                    raise e

            orders.append(row['orderID'])

        Order.objects.\
            filter(closed_at__isnull=True).\
            exclude(id__in=orders).\
            update(closed_at=parse_datetime(rowset['generatedAt']))


class Command(BaseCommand):

    def handle(self, *args, **options):
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)

        # Connect to the first publicly available relay.
        subscriber.connect(settings.EMDR_URL)
        # Disable filtering.
        subscriber.setsockopt(zmq.SUBSCRIBE, "")

        while True:
            job_json = subscriber.recv()
            market_json = zlib.decompress(job_json)
            market_data = simplejson.loads(market_json)

            if market_data['resultType'] == 'orders':
                processing.delay(market_data)
