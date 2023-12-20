from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from .models import Customer, Order, Product, Collection, OrderItem, ProductImage, Review, Cart, CartItem
from .pagination import DefaultPagination
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateOrderSerializer
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermission, ViewCustomerHistoryPermission


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images").all()
    # queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ["collection_id", "price"]
    filterset_class = ProductFilter
    search_fields = ["title", "description"]
    ordering_fields = ["price", "last_update"]
    # pagination_class = PageNumberPagination
    pagination_class = DefaultPagination
    permission_classes = (IsAdminOrReadOnly,)

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product=kwargs["pk"]).count() > 0:
            return Response(
                {"error": "This product object is cannot be deleted, becuase it is associated with some orderitems"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count("products")).all()
    serializer_class = CollectionSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection=kwargs["pk"]).count > 0:
            return Response(
                {"error": "Request collection object cannot be deleted, because it is associated with some of products"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(
        #   mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects \
            .select_related("product") \
            .filter(cart_id=self.kwargs["cart_pk"])

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (permissions.IsAdminUser,)
    # permission_classes = (FullDjangoModelPermission,)

    # def get_permissions(self):
    #     if self.request.method == "GET":
    #         return (permissions.AllowAny(),)
    #     return (permissions.IsAuthenticated(),)

    @action(detail=False, methods=["GET", "PUT"], permission_classes=(permissions.IsAuthenticated,))
    def me(self, request: Request):
        customer = Customer.objects.get(
            user_id=request.user.id, defaults={})
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request: Request, pk):
        return Response("ok")


class OrderViewSet(ModelViewSet):
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return (permissions.IsAdminUser(),)
        return (permissions.IsAuthenticated(),)

    def create(self, request: Request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        elif self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.prefetch_related("items__product").all()

        customer = Customer.objects.get(user_id=user.id)
        return Order.objects.prefetch_related("items__product").filter(customer_id=customer.id)


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


# class ProductViewSet(ModelViewSet):
#     serializer_class = ProductSerializer

#     def get_queryset(self):
#         queryset = Product.objects.all()
#         collection_id = self.request.query_params.get("collection_id")
#         if collection_id is not None:
#             try:
#                 queryset = queryset.filter(collection=collection_id)
#             except ValueError:
#                 pass
#         return queryset

#     def destroy(self, request, *args, **kwargs):
#         if OrderItem.objects.filter(product=kwargs["pk"]).count() > 0:
#             return Response(
#                 {"error": "This product object is cannot be deleted, becuase it is associated with some orderitems"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         return super().destroy(request, *args, **kwargs)


# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.select_related("collection").all()
#     serializer_class = ProductSerializer

#     def get_serializer_context(self):
#         return {"request": self.request}


# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def delete(self, request, pk):
#         product = get_object_or_404(
#             Product.objects.annotate(orderitems_count=Count("orderitems")).all(),
#             pk=pk)
#         if product.orderitems_count > 0:
#             return Response(
#                 {"error": "This product object is cannot be deleted, becuase it is associated with some orderitems"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response({"message": "Requested object deleted successfully"},status=status.HTTP_204_NO_CONTENT)


# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count("products")).all()
#     serializer_class = CollectionSerializer


# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count=Count("products")).all()
#     serializer_class = CollectionSerializer

#     def delete(self, request, pk):
#         collection = get_object_or_404(
#             Collection.objects.annotate(products_count=Count("products")).all(),
#             pk=pk)
#         if collection.products_count > 0:
#             return Response(
#                 {"error": "Request collection object cannot be deleted, because it is associated with some of products"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(
#             {"message": "Requested object has deleted"},
#             status=status.HTTP_204_NO_CONTENT)


# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related("collection").all()
#         serializer = ProductSerializer(queryset, many=True, context={"request": request})
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class ProductDetail(APIView):
#     def get_product_instance(self, id):
#         return get_object_or_404(Product, pk=id)

#     def get(self, request, id):
#         product = self.get_product_instance(id)
#         serializer = ProductSerializer(product, context={"request": request})
#         return Response(serializer.data)

#     def put(self, request, id):
#         product = self.get_product_instance(id)
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     def delete(self, request, id):
#         product = self.get_product_instance(id)
#         if product.orderitem_set.count() > 0:
#             return Response(
#                 {"error": "This product object is cannot be deleted, becuase it is associated with some orderitems"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response({"message": "Requested object deleted successfully"},status=status.HTTP_204_NO_CONTENT)


# @api_view(["GET", "POST"])
# def collection_list(request):
#     if request.method == "GET":
#         collections = Collection.objects.annotate(products_count=Count("products")).all()
#         serializer = CollectionSerializer(collections, many=True)
#         return Response(serializer.data)

#     elif request.method == "POST":
#         serializer = CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# @api_view(["GET", "PUT", "DELETE"])
# def collection_detail(request, pk):
#     collection = get_object_or_404(
#         Collection.objects.annotate(products_count=Count("products")).all(),
#         pk=pk)

#     if request.method == "GET":
#         selializer = CollectionSerializer(collection)
#         return Response(selializer.data)

#     elif request.method == "PUT":
#         serializer = CollectionSerializer(collection, request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     elif request.method == "DELETE":
#         if collection.product_set.count() > 0:
#             return Response(
#                 {"error": "Request collection object cannot be deleted, because it is associated with somo of products"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(
#             {"message": "Requested object has deleted"},
#             status=status.HTTP_204_NO_CONTENT)


# @api_view(["GET", "POST"])
# def product_list(request):
#     if request.method == "GET":
#         queryset = Product.objects.select_related("collection").all()
#         serializer = ProductSerializer(queryset, many=True, context={"request": request})
#         return Response(serializer.data)

#     elif request.method == "POST":
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     # elif request.method == "POST":
#     #     serializer = ProductSerializer(data=request.data)
#     #     if serializer.is_valid():
#     #         serializer.validated_data
#     #         return Response("ok")
#     #     else:
#     #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["GET", "PUT", "DELETE"])
# def product_detail(request, id):
#     product = get_object_or_404(Product, pk=id)

#     if request.method == "GET":
#         serializer = ProductSerializer(product, context={"request": request})
#         return Response(serializer.data)

#     elif request.method == "PUT":
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     elif request.method == "DELETE":
#         if product.orderitem_set.count() > 0:
#             return Response(
#                 {"error": "This product object is cannot be deleted, becuase it is associated with some orderitems"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response({"message": "Requested object deleted successfully"},status=status.HTTP_204_NO_CONTENT)

# @api_view()
# def product_detail(request, id):
#     try:
#         product = Product.objects.get(pk=id)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     except Product.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
