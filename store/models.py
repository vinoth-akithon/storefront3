from uuid import uuid4
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator

from store.validators import validate_file_size


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Product(models.Model):
    title = models.CharField(max_length=55)
    slug = models.SlugField(max_length=50, null=True)
    description = models.TextField(blank=True, default="")
    inventory = models.IntegerField(
        default=0, validators=[MinValueValidator(0)])
    price = models.DecimalField(
        default=0, max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])
    last_update = models.DateField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name="products")
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return self.title

    # class Meta:
    #     ordering = ["title"]


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="store/images/", validators=[validate_file_size])


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=255)
    description = models.TextField()
    reviewed_at = models.DateTimeField(auto_now_add=True)


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]
    phone = models.CharField(max_length=12)
    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.first_name + " " + self.user.last_name

    def first_name(self) -> str:
        return self.user.first_name

    def last_name(self) -> str:
        return self.user.last_name

    class Meta:
        ordering = ["user__first_name", "user__last_name"]
        permissions = [
            ("view_history", "Can view history")
        ]


class Order(models.Model):
    PENDING_STATUS = "P"
    COMPLETE_STATUS = "C"
    FAILED_STATUS = "F"
    PAYMENT_STATUS_CHOICES = [
        (PENDING_STATUS, "Pending"),
        (COMPLETE_STATUS, "Complete"),
        (FAILED_STATUS, "Failed")
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PENDING_STATUS)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    def get_customer_name(self):
        return self.customer.first_name + " " + self.customer.last_name

    def __str__(self) -> str:
        return f"Order-{self.id}"

    class Meta:
        # ordering = ["id"]
        permissions = [
            ("cancel_order", "Can cancel order")
        ]


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=55, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orderitems")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    class Meta:
        unique_together = [["cart", "product"]]

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f"{self.product}"
