from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
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


class OrderChangeInline(admin.TabularInline):
    model = OrderChange
    readonly_fields = ('price', 'vol_remaining', 'issue_date', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'bid', 'item_type', 'range', 'region', 'solar_system', 'station')
    readonly_fields = ('item_type', 'bid', 'range', 'duration', 'vol_entered', 'min_volume', 'region', 'station', 'solar_system', 'created_at')
    inlines = [
        OrderChangeInline,
    ]
    search_fields = ('item_type__name', 'solar_system__name', 'station__name')
    list_filter = ('bid', 'region')

admin.site.register(Order, OrderAdmin)


class OrderChangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'price', 'vol_remaining', 'issue_date')
    readonly_fields = ('order', 'price', 'vol_remaining', 'issue_date', 'created_at')

admin.site.register(OrderChange, OrderChangeAdmin)


class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    fields = ('name', 'value')
    readonly_fields = ('name', 'value')

admin.site.register(State, StateAdmin)