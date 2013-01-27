from django.contrib import admin
from eve.models import ItemType, Station, SolarSystem, Region, Order, OrderChange, State


class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(ItemType, ItemTypeAdmin)

class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'solar_id')

admin.site.register(Station, StationAdmin)

class SolarSystemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(SolarSystem, SolarSystemAdmin)

class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(Region, RegionAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'bid', 'item_type')

admin.site.register(Order, OrderAdmin)

class OrderChangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'price', 'vol_remaining', 'issue_date')

admin.site.register(OrderChange, OrderChangeAdmin)

class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    fields = ('name', 'value')
    readonly_fields = ('name', 'value')

admin.site.register(State, StateAdmin)