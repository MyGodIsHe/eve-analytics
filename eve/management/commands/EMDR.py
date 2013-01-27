"""
API: https://eve-market-data-relay.readthedocs.org/en/latest/
Data Format: http://dev.eve-central.com/unifieduploader/start
"""
from datetime import datetime, timedelta
import random
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import zlib
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime
from eve.models import Order, OrderChange, ItemType, Region, Station, SolarSystem, State

import zmq.green as zmq
from django.utils import simplejson
from multiprocessing import Process, Queue
import re


class Worker(object):

    def __init__(self):
        self.queue = Queue()
        self.process = Process(target=Worker.target, args=(self.queue,))
        self.process.start()

        self.packages = 0
        self.skip_packages = 0

        self.last_time = datetime.now()

    def update_stats(self):
        current_time = datetime.now()
        if current_time - self.last_time > timedelta(seconds=1):
            self.last_time = current_time
            State.set_value('emdr-queue-size', self.queue.qsize())
            State.set_value('emdr-skip-percent', "%.2f%%" % (100.0 * self.skip_packages / self.packages))

    @staticmethod
    @transaction.commit_manually
    def target(queue):
        """
        Run in subprocess
        """
        last_time = datetime.now()
        while True:
            Worker.processing(queue.get())
            current_time = datetime.now()
            if current_time - last_time > timedelta(seconds=settings.EMDR_TRANSACTION_INTERVAL):
                last_time = current_time
                State.set_value('emdr-last-transaction', last_time)
                transaction.commit()

    @staticmethod
    def try_save(order):
        counter = 0
        while counter < 10:
            try:
                order.save()
                break
            except IntegrityError as e:
                if e.args[0] != 1452:
                    raise e
                result = re.search(r'FOREIGN KEY \(`(\w+)`\)', e.args[1])
                if not result:
                    raise e
                result = result.group(1)
                if result == 'item_type_id':
                    ItemType(id=order.item_type_id).save()
                elif result == 'station_id':
                    Station(id=order.station_id).save()
                elif result == 'region_id':
                    Region(id=order.region_id).save()
                elif result == 'solar_system_id':
                    SolarSystem(id=order.solar_system_id, region_id=order.region_id).save()
                else:
                    raise e
            counter += 1

    @staticmethod
    def get_region(market_data):
        region_id = None
        for rowset in market_data['rowsets']:
            if rowset['regionID']:
                region_id = rowset['regionID']
                break
        if not region_id:
            return

        return region_id

    @staticmethod
    def processing_row(rowset, row, region_id):
        issue_date = parse_datetime(row['issueDate'])

        if not Order.objects.filter(id=row['orderID']).count():
            order = Order(
                id=row['orderID'],
                bid=row['bid'],
                range=row['range'],
                duration=row['duration'],
                vol_entered=row['volEntered'],
                min_volume=row['minVolume'],
                region_id=region_id,
                item_type_id=rowset['typeID'],
                station_id=row['stationID'],
            )
            if row['solarSystemID']:
                order.solar_system_id = row['solarSystemID']
            Worker.try_save(order)

        try:
            OrderChange(
                order_id=row['orderID'],
                price=row['price'],
                vol_remaining=row['volRemaining'],
                issue_date=issue_date,
            ).save()
        except IntegrityError as e:
            if e.args[0] != 1062:
                raise e

    @staticmethod
    def processing(market_data):
        """
        Run in subprocess
        """
        region_id = Worker.get_region(market_data)
        if not region_id:
            return

        for rowset in market_data['rowsets']:
            orders = []

            for row in rowset['rows']:
                row = dict(zip(market_data['columns'], row))
                Worker.processing_row(rowset, row, region_id)
                orders.append(row['orderID'])

            Order.objects.\
                filter(closed_at__isnull=True).\
                exclude(id__in=orders).\
                update(closed_at=parse_datetime(rowset['generatedAt']))


class Command(BaseCommand):

    def start_worker(self):
        worker = Worker()

        # subscribe
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)
        subscriber.connect(settings.EMDR_URL)
        subscriber.setsockopt(zmq.SUBSCRIBE, "")

        try:
            while True:
                job_json = subscriber.recv()
                market_json = zlib.decompress(job_json)
                market_data = simplejson.loads(market_json)

                if market_data['resultType'] == 'orders':
                    worker.packages += 1
                    if random.randint(0, worker.queue.qsize() / 100) != 0:
                        worker.skip_packages += 1
                        continue
                    worker.queue.put(market_data)
                    worker.update_stats()
        except KeyboardInterrupt:
            print "Caught KeyboardInterrupt, terminating workers"
            worker.queue.close()
            worker.process.terminate()
        except Exception as e:
            worker.queue.close()
            worker.process.terminate()
            raise e


    def handle(self, *args, **options):
        print "Start EMDR"
        self.start_worker()