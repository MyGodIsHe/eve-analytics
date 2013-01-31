"""
API: https://eve-market-data-relay.readthedocs.org/en/latest/
Data Format: http://dev.eve-central.com/unifieduploader/start
"""
import random
import re
from datetime import datetime, timedelta
from multiprocessing import Process, Queue
import zlib
import signal
import sys
import zmq.green as zmq

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime
from django.utils.timezone import utc
from django.utils import simplejson

from eve.models import Order, OrderChange, ItemType, Region, Station, SolarSystem, State, SkipChart


tz_now = lambda: datetime.utcnow().replace(tzinfo=utc)


class DataStore(object):
    QUEUE_SIZE_LIMIT = getattr(settings, 'QUEUE_SIZE_LIMIT', 1000)
    TD_UPDATE_STATE = getattr(settings, 'TD_UPDATE_STATE', timedelta(minutes=1))
    TD_SKIP_BY_KEY = getattr(settings, 'TD_SKIP_BY_KEY', timedelta(minutes=10))

    def __init__(self):
        self.__rowsets = {}
        self.news = Queue()

        self.process = Process(target=DataStore.entry_point, args=(self.news, ))
        self.process.start()

        self.packages = 0
        self.skip_packages = 0
        self.last_time_null = tz_now()

    def put(self, market_data):
        region_id = None
        for rowset in market_data['rowsets']:
            if rowset['regionID']:
                region_id = rowset['regionID']
                break
        if not region_id:
            return

        now = tz_now()

        for rowset in market_data['rowsets']:
            data_key = (region_id, rowset['typeID'])
            rowset['columns'] = market_data['columns']
            rowset['regionID'] = region_id

            if data_key in self.__rowsets and\
               now - self.__rowsets[data_key] < DataStore.TD_SKIP_BY_KEY:
                continue

            self.__rowsets[data_key] = now

            if not self.need_skip():
                self.news.put(rowset)

        self.update_stats()

    def update_stats(self):
        current_time = tz_now()
        if current_time - self.last_time_null > DataStore.TD_UPDATE_STATE:
            self.last_time_null = current_time
            last_percent = 100.0 * self.skip_packages / self.packages
            self.packages = 0
            self.skip_packages = 0
            SkipChart.objects.create(percent=last_percent, queue_size=self.news.qsize())

    def close(self):
        self.process.terminate()
        self.news.close()

    def need_skip(self):
        self.packages += 1
        if random.randint(0, self.news.qsize() / DataStore.QUEUE_SIZE_LIMIT) != 0:
            self.skip_packages += 1
            return True
        return False

    @staticmethod
    @transaction.commit_manually
    def entry_point(news):
        td_interval = timedelta(seconds=10)
        worker = Worker()
        last_time = tz_now()
        while True:
            worker.processing(news.get())
            current_time = tz_now()
            if current_time - last_time > td_interval:
                last_time = current_time
                transaction.commit()
                State.set_value('emdr-last-transaction', last_time)
                transaction.commit()


class Worker(object):
    """
    Run in subprocess
    """

    def __init__(self):
        self.data_dict = {}

    def try_save(self, order):
        counter = 0
        while counter < 10:
            try:
                order.save()
                break
            except IntegrityError as e:
                if e.args[0] != 1452:
                    raise
                result = re.search(r'FOREIGN KEY \(`(\w+)`\)', e.args[1])
                if not result:
                    raise
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
                    raise
            counter += 1

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

    def processing(self, rowset):
        orders = []

        for row in rowset['rows']:
            row = dict(zip(rowset['columns'], row))
            self.processing_row(rowset, row, rowset['regionID'])
            orders.append(row['orderID'])

        Order.objects.\
            filter(region_id=rowset['regionID'],
                item_type_id=rowset['typeID'],
                closed_at__isnull=True).\
            exclude(id__in=orders).\
            update(closed_at=parse_datetime(rowset['generatedAt']))


class WorkManager(object):

    def __init__(self):
        self.data_store = DataStore()

        # subscribe
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.connect(settings.EMDR_URL)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "")

    def loop(self):
        def terminate(signnum, frame):
            print "Terminating workers"
            self.data_store.close()
            sys.exit()
        signal.signal(signal.SIGTERM, terminate)

        try:
            while True:
                job_json = self.subscriber.recv()
                market_json = zlib.decompress(job_json)
                market_data = simplejson.loads(market_json)

                if market_data['resultType'] == 'orders':
                    self.data_store.put(market_data)
        except (KeyboardInterrupt, SystemExit):
            print "Terminating workers"
            self.data_store.close()
        except Exception:
            self.data_store.close()
            raise


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "EMDR Start Time: %s" % tz_now().strftime('%Y-%m-%d %H:%M')
        WorkManager().loop()