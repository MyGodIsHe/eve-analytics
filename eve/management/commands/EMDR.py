"""
API: https://eve-market-data-relay.readthedocs.org/en/latest/
Data Format: http://dev.eve-central.com/unifieduploader/start
"""
import random
import re
from datetime import datetime, timedelta
from multiprocessing import Process, Queue
import zlib
import zmq.green as zmq

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime
from django.utils.timezone import utc
from django.utils import simplejson

from eve.models import Order, OrderChange, ItemType, Region, Station, SolarSystem, State


tz_now = lambda: datetime.utcnow().replace(tzinfo=utc)


class Worker(object):
    """
    Run in subprocess
    """
    TD_LAST_UPDATE = timedelta(minutes=10)

    def __init__(self):
        self.last_update_dict = {}

    def try_save(self, order):
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

    def get_region_id(self, market_data):
        region_id = None
        for rowset in market_data['rowsets']:
            if rowset['regionID']:
                region_id = rowset['regionID']
                break
        if not region_id:
            return

        return region_id

    def processing_row(self, rowset, row, region_id):
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
            self.try_save(order)

        is_double = OrderChange.objects.filter(
            order_id=row['orderID'],
            price=row['price'],
            vol_remaining=row['volRemaining'],
        ).count()
        if not is_double:
            OrderChange(
                order_id=row['orderID'],
                price=row['price'],
                vol_remaining=row['volRemaining'],
                issue_date=issue_date,
            ).save()

    def need_update(self, region_id, type_id):
        update_key = (region_id, type_id)
        if update_key not in self.last_update_dict:
            pass
        elif tz_now() - self.last_update_dict[update_key] < Worker.TD_LAST_UPDATE:
            return False


        self.last_update_dict[update_key] = tz_now()

        return True

    def processing(self, market_data):
        region_id = self.get_region_id(market_data)
        if not region_id:
            return

        for rowset in market_data['rowsets']:
            if not self.need_update(region_id, rowset['typeID']):
                continue

            orders = []

            for row in rowset['rows']:
                row = dict(zip(market_data['columns'], row))
                self.processing_row(rowset, row, region_id)
                orders.append(row['orderID'])

            Order.objects.\
                filter(region_id=region_id,
                    item_type_id=rowset['typeID'],
                    closed_at__isnull=True).\
                exclude(id__in=orders).\
                update(closed_at=parse_datetime(rowset['generatedAt']))

    @staticmethod
    @transaction.commit_manually
    def entry_point(queue):
        td_interval = timedelta(seconds=10)
        worker = Worker()
        last_time = tz_now()
        while True:
            worker.processing(queue.get())
            current_time = tz_now()
            if current_time - last_time > td_interval:
                last_time = current_time
                transaction.commit()
                State.set_value('emdr-last-transaction', last_time)
                transaction.commit()


class WorkManager(object):
    TD_QUEUE_SIZE = timedelta(seconds=1)
    TD_SKIP_PERCENT = timedelta(minutes=1)
    QUEUE_SIZE_LIMIT = 1000

    def __init__(self):
        self.queue = Queue()
        self.process = Process(target=Worker.entry_point, args=(self.queue,))
        self.process.start()

        self.skip_percent_list = []
        self.packages = 0
        self.skip_packages = 0
        self.last_time_null = tz_now()
        self.last_time = tz_now()

        # subscribe
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.connect(settings.EMDR_URL)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "")

    def need_skip(self):
        self.packages += 1
        if random.randint(0, self.queue.qsize() / WorkManager.QUEUE_SIZE_LIMIT) != 0:
            self.skip_packages += 1
            return True
        return False

    def update_stats(self):
        current_time = tz_now()
        if current_time - self.last_time > WorkManager.TD_QUEUE_SIZE:
            self.last_time = current_time
            State.set_value('emdr-queue-size', self.queue.qsize())

            if current_time - self.last_time_null > WorkManager.TD_SKIP_PERCENT:
                self.last_time_null = current_time
                last_percent = 100.0 * self.skip_packages / self.packages
                self.skip_percent_list.append(last_percent)
                self.skip_percent_list = self.skip_percent_list[-60:]
                self.packages = 0
                self.skip_packages = 0
                percent = sum(self.skip_percent_list) / len(self.skip_percent_list)
                State.set_value('emdr-skip-percent-hour', "%.2f%%" % percent)
                State.set_value('emdr-skip-percent-minute', "%.2f%%" % last_percent)

    def loop(self):
        try:
            while True:
                job_json = self.subscriber.recv()
                market_json = zlib.decompress(job_json)
                market_data = simplejson.loads(market_json)

                if market_data['resultType'] == 'orders':
                    if self.need_skip():
                        continue
                    self.queue.put(market_data)
                    self.update_stats()
        except KeyboardInterrupt:
            print "Caught KeyboardInterrupt, terminating workers"
            self.queue.close()
            self.process.terminate()
        except Exception as e:
            self.queue.close()
            self.process.terminate()
            raise e


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "EMDR Start Time: %s" % tz_now().strftime('%Y-%m-%d %H:%M')
        WorkManager().loop()