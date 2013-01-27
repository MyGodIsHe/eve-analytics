from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render
from eve.models import ItemType, Order


def home(request):
    return null_orders(request)


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
    return render(request, 'eve/home.html', {
        'page': p.page(page),
    })