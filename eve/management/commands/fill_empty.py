from django.core.management.base import BaseCommand, CommandError

from eve.models import ItemType, Region, Station, SolarSystem



class Command(BaseCommand):


    def handle(self, *args, **options):
        SLICE_LEN = 250
        print "Start Fill Empty"
        print
        print "Update ItemType:",
        print ItemType.resolve_all_empty(SLICE_LEN)
        print
        print "Update Region:",
        print Region.resolve_all_empty(SLICE_LEN)
        print
        print "Update Solar System:",
        print SolarSystem.resolve_all_empty(SLICE_LEN)
        print
        print "Update Station:",
        print Station.resolve_all_empty(SLICE_LEN)
        print