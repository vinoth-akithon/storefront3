from django_filters.rest_framework import FilterSet
from store.models import Product

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        # fields = ["collection"]
        fields = {
            "collection": ["exact"],
            "price": ["gt", "lt"]
        }