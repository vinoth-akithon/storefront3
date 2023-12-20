from datetime import datetime
from pprint import pprint
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value, Func, ExpressionWrapper, ValueRange, Manager
from django.db.models.aggregates import Count, Avg, Max, Min, Sum
from django.db.models.functions import Concat
from django.db.models.fields import DecimalField, IntegerField, CharField
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection

from store.models import Collection, Customer, Order, OrderItem, Product
from tag.models import TagItem
from .tasks import long_running_task
import requests
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
import logging

logger = logging.getLogger(__name__)


class Index(APIView):

    # @method_decorator(cache_page(10*60))
    def get(self, request):
        logger.debug("API is calling")
        logger.info("API is calling")
        logger.warning("API is calling")
        logger.error("API is calling")
        logger.critical("API is calling")
        response = requests.get("https://httpbin.org/delay/2")
        data = response.json()
        return render(request, "index.html", context={"result": f"Hello {data}"})


# @cache_page(10*60)
# def index(request: HttpRequest):
#     response = requests.get("https://httpbin.org/delay/2")
#     data = response.json()
#     return render(request, "index.html", context={"result": f"Hello {data}"})


# def index(request: HttpRequest):
#     key = "httpbin"
#     if cache.get(key) is None:
#         response = requests.get("https://httpbin.org/delay/2")
#         data = response.json()
#         cache.set(key, data, timeout=10*60)
#     return render(request, "index.html", context={"result": f"Hello {cache.get(key)}"})


# def index(request: HttpRequest):
#     print(type(long_running_task))
#     long_running_task.delay()
#     return render(request, "index.html")


@transaction.atomic()
def say_hello(request):
    # products = Product.objects.filter(id__in=OrderItem.objects.values('product').distinct()).values('id', 'title').order_by('title')
    # products = Product.objects.select_related('collection')
    # order_items = OrderItem.objects.filter(order_id__in=Order.objects.values("id").order_by('-id')[:5])
    # order_items = OrderItem.objects.order_by('-id')
    # orders = Order.objects.select_related('customer').order_by('-placed_at')[:3].prefetch_related("orderitem_set__product").values()
    # result = OrderItem.objects.filter(product_id=1).aggregate(total_unit=Sum("quantity"))
    # result = Product.objects.filter(collection=3).aggregate(
    #     total_product=Count("id"),
    #     min_price=Min("price"),
    #     max_price=Max("price"),
    #     average_price=Avg("price"))
    # result = Product.objects.annotate(status=Value(1)+1)
    # result = Customer.objects.annotate(full_name=Func(F('first_name'), Value(" "), F('last_name'), function='concat'))
    # result = Customer.objects.annotate(full_name=Concat("first_name", Value(" + "), "last_name"))
    # result = Customer.objects.annotate(full_name=Func(Value(" "), F("first_name"), F("last_name"), function="concat_ws"))
    # result = Customer.objects.annotate(new_field=F("first_name"), orders_count=Count("order"))
    # result = Product.objects.annotate(discount=ExpressionWrapper(F("price") * 2.5, output_field=CharField()))
    # content_type = ContentType.objects.get_for_model(Product)
    # result = TagItem.objects \
    #     .select_related("tag") \
    #     .filter(
    #         content_type=content_type,
    #         object_id=1
    #     )
    # result = TagItem.objects.get_tags_for(Product, 1)

    # creating object
    # collection = Collection(title="Test Collection", featured_product=Product(pk=1))

    # collection = Collection()
    # collection.title = "Test Collection"
    # collection.featured_product = Product(pk=1)

    # collection.save()
    # print(collection.id)
    # result = collection

    # collection = Collection.objects.create(title="Test Collection", featured_product=Product(pk=1))

    # updating object
    # collection = Collection(pk=19)
    # collection.title = "Test collection"
    # collection.featured_product = None
    # collection.save()

    # result = Collection.objects.filter(pk=21).update(featured_product=None)

    # Deleting object
    # collection = Collection(pk=19)
    # collection.delete()

    # collection = Collection.objects.filter(pk=21).delete()

    # Transaction using context manager
    # with transaction.atomic():
    # order = Order()
    # order.placed_at = datetime.now()
    # order.customer = Customer(pk=1)
    # order.save()

    # order_item = OrderItem()
    # order_item.order = 100000000

    # performing raw queries
    # product = Product.objects.raw("select id, first_name from store_customer")
    # for i in product:
    #     print(i.first_name)

    with connection.cursor() as cursor:
        cursor.execute("select * from store_customer limit 5")
        print(cursor.fetchall())

    return render(
        request,
        "index.html",
        {
            "name": "vinoth",
            # "products": list(products)
            "result": "result"
        })
