from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models

# Register your models here.


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]

    def products_count(self, collection):
        url = (reverse("admin:store_product_changelist")
               + "?" +
               urlencode(
                   {"collection__id": collection.id}
        ))
        return format_html("<a href={}>{}</a>", url, collection.products_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count("products"))


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ["product"]
    min_num = 1
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]
    list_per_page = 10
    list_display = ["order_id", "customer_name"]
    list_select_related = ["customer"]
    ordering = ["id"]

    def order_id(self, order):
        return order

    def customer_name(self, order):
        return order.get_customer_name()


class InventoryFilter(admin.SimpleListFilter):
    title = "Inventory"
    parameter_name = "inventory"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ("less_than_10", "Low")
        ]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == "less_than_10":
            return queryset.filter(inventory__lt=10)


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ["thumnail"]
    extra = 0

    def thumnail(self, instance):
        if instance.image.name != "":
            return format_html(f"<img src='{instance.image.url}' class='thumnail'>")
        return ""


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ["clear_inventory"]
    list_display = ["title", "price", "inventory_status",
                    "collection", "collection_featured_product"]
    list_per_page = 10
    list_select_related = ["collection"]
    list_filter = ["collection", "last_update", InventoryFilter]
    search_fields = ["title"]
    inlines = [ProductImageInline]

    @admin.display(ordering="inventory")
    def inventory_status(self, x) -> str:
        if x.inventory > 10:
            return "Ok"
        return "Low"

    def collection_featured_product(self, product):
        return product.collection.featured_product

    @admin.action()
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(request, f"{update_count} were updated successfully",
                          messages.ERROR
                          )

    class Media:
        css = {
            "all": ["store/style.css"]
        }


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    # readonly_fields = ["last_name"]
    # exclude = ["first_name"]
    # prepopulated_fields = {
    #     "last_name": ["first_name"]
    # }
    list_display = ["first_name", "last_name", "membership", "total_orders"]
    list_editable = ["membership"]
    list_per_page = 10
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    def total_orders(self, customer):
        url = (reverse("admin:store_order_changelist")
               + "?" +
               urlencode({
                   "customer__id": customer.id
               }))
        return format_html("<a href='{}'>{}</a>", url, customer.total_orders)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(total_orders=Count("order"))
