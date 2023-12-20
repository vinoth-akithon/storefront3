from store.signals import order_created
from django.dispatch import receiver


@receiver(order_created)
def order_created_successfully(sender, **kwargs):
    print(kwargs["order"])
