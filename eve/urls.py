from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'eve.views.home', name='home'),
    url(r'^test/$', 'eve.views.test'),
    url(r'^null_orders/page(?P<page>\d+)/$', 'eve.views.null_orders', name='null_orders'),
    url(r'^get_skip_data/$', 'eve.views.get_skip_data', name='get_skip_data'),
    (r'^admin/django_rq/', include('django_rq.urls')),
    (r'^admin/grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
)