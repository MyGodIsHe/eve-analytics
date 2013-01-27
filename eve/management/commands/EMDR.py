"""
API: https://eve-market-data-relay.readthedocs.org/en/latest/
Data Format: http://dev.eve-central.com/unifieduploader/start
"""
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import zlib
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime
from eve.models import Order, OrderChange, ItemType, Region, Station, SolarSystem, Stat

import zmq.green as zmq
from django.utils import simplejson
from multiprocessing import Process, Queue


def worker(queue):
    while True:
        processing(queue.get())

def processing(market_data):
    region_id = None
    for rowset in market_data['rowsets']:
        if rowset['regionID']:
            region_id = rowset['regionID']
            break
    if not region_id:
        return

    #region = Region.objects.get_or_create(id=region_id)[0]

    for rowset in market_data['rowsets']:
        orders = []

        for row in rowset['rows']:
            row = dict(zip(market_data['columns'], row))

            issue_date = parse_datetime(row['issueDate'])


#            if not Order.objects.filter(id=row['orderID']).count():
#                order = Order(
#                    id=row['orderID'],
#                    bid=row['bid'],
#                    range=row['range'],
#                    duration=row['duration'],
#                    vol_entered=row['volEntered'],
#                    min_volume=row['minVolume'],
#                    region=region,
#                )
#                order.item_type = ItemType.objects.get_or_create(id=rowset['typeID'])[0]
#                order.station = Station.objects.get_or_create(id=row['stationID'])[0]
#                if row['solarSystemID']:
#                    order.solar_system = SolarSystem.objects.get_or_create(
#                        id=row['solarSystemID'], defaults={'region_id':region_id})[0]
#                order.save()
#
#            try:
#                OrderChange(
#                    order_id=row['orderID'],
#                    price=row['price'],
#                    vol_remaining=row['volRemaining'],
#                    issue_date=issue_date,
#                ).save()
#            except IntegrityError as e:
#                if e.args[0] != 1062:
#                    raise e
#
#            orders.append(row['orderID'])

#        Order.objects.\
#            filter(closed_at__isnull=True).\
#            exclude(id__in=orders).\
#            update(closed_at=parse_datetime(rowset['generatedAt']))


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "Start EMDR"

        # worker
        queue = Queue()
        process = Process(target=worker, args=(queue,))
        process.start()

        # subscribe
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)
        subscriber.connect(settings.EMDR_URL)
        subscriber.setsockopt(zmq.SUBSCRIBE, "")

        last_time = datetime.now()

        while True:
            job_json = subscriber.recv()
            market_json = zlib.decompress(job_json)
            market_data = simplejson.loads(market_json)

            if market_data['resultType'] == 'orders':
                queue.put(market_data)
                current_time = datetime.now()
                if current_time - last_time > timedelta(seconds=1):
                    last_time = current_time
                    Stat.set_value('emdr-queue-size', queue.qsize())