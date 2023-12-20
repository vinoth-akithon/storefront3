from django.urls import path, include
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from . import views


# router = SimpleRouter()
router = DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet, basename="collections")
router.register("carts", views.CartViewSet, basename="carts")
router.register("customers", views.CustomerViewSet, basename="customers")
router.register("orders", views.OrderViewSet, basename="orders")

products_router = NestedDefaultRouter(router, "products", lookup="product")
products_router.register("reviews", views.ReviewViewSet,
                         basename="product-reviews")
products_router.register(
    "images", views.ProductImageViewSet, basename="product-images")

carts_router = NestedDefaultRouter(router, "carts", lookup="cart")
carts_router.register("items", views.CartItemViewSet, basename="cart-items")


urlpatterns = router.urls + products_router.urls + carts_router.urls

# router.urls

# urlpatterns = [
#     path("products/", views.ProductList.as_view()),
#     path("products/<int:pk>/", views.ProductDetail.as_view()),
#     path("collections/", views.CollectionList.as_view()),
#     path("collections/<int:pk>/", views.CollectionDetail.as_view(), name="collection-detail")
# ]
