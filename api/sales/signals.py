from django.db.models.signals import post_save
from django.dispatch import receiver
from api.sales.models import SaleItem


@receiver(post_save, sender=SaleItem)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product
    if product.quantity >= instance.quantity:
        product.quantity -= instance.quantity
        product.save()
    else:
        raise ValueError(f"Not enough stock for product {product.name}")
