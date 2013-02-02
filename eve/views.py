import datetime
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import simplejson
from django.utils.dateparse import parse_datetime
from django.views.decorators.cache import never_cache
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import ugettext as _
import time

from eve.models import ItemType, Order, State, OrderChange, SkipChart
from eve.forms import EveAuthenticationForm


@never_cache
def sign_out(request):
    """
    Logs out the user for the given HttpRequest.

    This should *not* assume the user is already logged in.
    """
    from django.contrib.auth.views import logout
    return logout(request, current_app='eve', template_name='eve/sign_out.html')

@never_cache
def sign_in(request):
    """
    Displays the login form for the given HttpRequest.
    """
    from django.contrib.auth.views import login
    context = {
        'app_path': request.get_full_path(),
        REDIRECT_FIELD_NAME: request.get_full_path(),
        }
    defaults = {
        'extra_context': context,
        'current_app': 'eve',
        'authentication_form': EveAuthenticationForm,
        'template_name': 'eve/sign_in.html',
        }
    return login(request, **defaults)


def home(request):
    if request.user.is_anonymous():
        return sign_in(request)

    active_orders = Order.objects.filter(closed_at__isnull=True)
    State.set_value('order-buy-count', active_orders.filter(bid=True).count())
    State.set_value('order-sell-count', active_orders.filter(bid=False).count())
    State.set_value('order-closed-count', Order.objects.filter(closed_at__isnull=False).count())
    return render(request, 'eve/home.html', {
        'state_list': State.objects.order_by('name'),
        })


def null_orders(request, page=1):
    null_orders = ItemType.objects.extra(
        select={
            'buy_count': 'SELECT COUNT(*) FROM t1 WHERE t1.item_type_id = t2.id and t1.type = %s' % Order.TYPE_BUY,
            'sell_count': 'SELECT COUNT(*) FROM t1 WHERE t1.item_type_id = t2.id and t1.type = %s' % Order.TYPE_SELL,
        },
        tables=[
           '"%s" AS "t1"' % Order._meta.db_table,
           '"%s" AS "t2"' % ItemType._meta.db_table,
       ],
        where=['buy_count = 0 or sell_count = 0'],
    )
    p = Paginator(null_orders, 20)
    p._count = null_orders.aggregate(Count('id'))
    return render(request, 'eve/null_orders.html', {
        'page': p.page(page),
    })


def get_skip_data(request):
    last_time = request.GET.get('last_time', None)
    max_count = request.GET.get('max_count', None)
    try:
        max_count = int(max_count)
    except (ValueError, TypeError):
        return HttpResponseBadRequest()
    if max_count < 0:
        return HttpResponseBadRequest()

    create_at = parse_datetime(last_time)
    if not create_at:
        return HttpResponseBadRequest()
    query = SkipChart.objects.filter(create_at__gt=create_at)
    query = query.order_by('-id')[:max_count]
    data = query.values_list('create_at', 'package_percent', 'row_percent', 'queue_size')
    data = [(str(i[0]), i[1:]) for i in data]
    data.reverse()
    return HttpResponse(simplejson.dumps(data), mimetype="application/json")


def test(request):
    return render(request, 'eve/test.html')