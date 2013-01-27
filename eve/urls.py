from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'eve.views.home', name='home'),
    url(r'^null_orders/page(?P<page>\d+)/$', 'eve.views.null_orders', name='null_orders'),
    (r'^admin/django_rq/', include('django_rq.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),
)