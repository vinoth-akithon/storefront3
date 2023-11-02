from django.db import models


class Collection(models.Model):
    title = models.CharField(max_length=255)


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Product(models.Model):
    title = models.CharField(max_length=55)
    slug = models.SlugField(max_length=50, null=True)
    description = models.TextField()
    inventory = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    last_update = models.DateField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion)


class Customer(models.Model):
    first_name = models.CharField(max_length=55)
    last_name = models.CharField(max_length=55)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12)
    birth_date = models.DateField(null=True)


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
    
# One to one relationship example
# class Address(models.Model):
#     street = models.CharField(max_length=255)
#     city = models.CharField(max_length=255)
#     customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)

# One to many relationship example
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=55, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

