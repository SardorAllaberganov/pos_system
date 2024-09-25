from django.db.models.signals import post_save
from django.dispatch import receiver
from api.sales.models import SaleItem, Sale, Receipt
import uuid


@receiver(post_save, sender=SaleItem)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product
    if product.quantity >= instance.quantity:
        product.quantity -= instance.quantity
        product.save()
    else:
        raise ValueError(f"Not enough stock for product {product.name}")


@receiver(post_save, sender=Sale)
def add_loyalty_points(sender, instance, created, **kwargs):
    if created:
        customer = instance.customer
        loyalty_points_earned = instance.total_amount / 100
        customer.loyalty_points += loyalty_points_earned
        customer.save()


@receiver(post_save, sender=Sale)
def generate_receipt_after_sale(sender, instance, created, **kwargs):
    if created:
        receipt_number = f"REC-{uuid.uuid4().hex[:8].upper()}"

        Receipt.objects.create(
            sale=instance,
            receipt_number=receipt_number,
            cashier=instance.cashier,
            customer=instance.customer,
            total_amount=instance.total_amount,
            payment_type=instance.payment_type,
        )
