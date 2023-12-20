from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from store.models import Customer, Order, OrderItem, Product, Collection, ProductImage, Review, Cart, CartItem
from .signals import order_created


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "title", "products_count"]

    products_count = serializers.IntegerField(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]

    def save(self, **kwargs):
        return super().save(product_id=self.context["product_id"], **kwargs)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        """
        model: Here the model refer which database model 
        fields: need to include which should be present in
                external world(via api).
                the django rest framwork will look the field
                in model defination and and look into serializer 
                defination.
        """
        model = Product
        fields = ["id", "title", "description", "price",
                  "price_with_tax", "collection", "inventory", "images"]

    id = serializers.IntegerField(read_only=True)
    price_with_tax = serializers.SerializerMethodField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    def get_price_with_tax(self, obj: Product):
        return obj.price * Decimal(1.1)

    # def get_image(self, )


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "reviewed_at", "name", "description"]

    # product_id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        print(validated_data)
        return Review.objects.create(product_id=self.context["product_id"], **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]

    def create(self, validated_data):
        return CartItem.objects.create(cart_id=self.context.get("cart_id"), **validated_data)


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid product id found")
        return value

    def save(self, **kwargs):
        cart_id = self.context.get("cart_id")
        product_id = self.validated_data.get("product_id")
        quantity = self.validated_data.get("quantity")

        try:
            cart_item = CartItem.objects.get(cart=cart_id, product=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # Create new CartItem object
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)
        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "quantity", "unit_price", "product"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "placed_at", "payment_status", "items"]


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["payment_status"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                "No card was found for the given id.")
        elif not CartItem.objects.filter(cart_id=cart_id).count():
            raise serializers.ValidationError("The cart is empty.")
        return cart_id

    def save(self, **kwargs):
        user_id = self.context["user_id"]
        cart_id = self.validated_data["cart_id"]

        with transaction.atomic():
            customer = Customer.objects\
                .get(user_id=user_id)
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects \
                                 .select_related("product") \
                                 .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.price,
                    quantity=item.quantity
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(id=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)
        return order


# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)


# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=5, decimal_places=2)
#     # price_with_tax = serializers.SerializerMethodField(method_name="getting_price_with_tax")
#     price_with_tax = serializers.SerializerMethodField() # example for custom serializer field using serializermethod
#     unit_price = serializers.DecimalField(max_digits=5, decimal_places=2, source="price") # Example for name alise for internal representation
#     # collection = serializers.PrimaryKeyRelatedField(
#     #     queryset=Collection.objects.all() # Example for getting primarykey of the related object
#     # )
#     # collection = serializers.StringRelatedField() # Example for string representation of ralated object
#     # collection = CollectionSerializer() # Example for nested object representation of related object
#     collection = serializers.HyperlinkedRelatedField(
#         view_name="collection-detail",
#         queryset=Collection.objects.all())


#     def get_price_with_tax(self, obj: Product):
#         return obj.price * Decimal(1.1)

#     # def getting_price_with_tax(self, obj: Product):
#     #     return obj.price * Decimal(1.1)
