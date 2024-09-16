from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from api.product.models import Product
from api.supplier.models import PurchaseOrder, PurchaseOrderItem
import os


@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Product.objects.get(pk=instance.pk)
        except Product.DoesNotExist:
            return
        old_product_image = old_instance.product_image
        if old_product_image and old_product_image != instance.product_image:
            old_image_path = old_product_image.path
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)


@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.product_image:
        instance.product_image.delete(False)


@receiver(post_save, sender=Product)
def create_or_update_purchase_order(sender, instance, created, **kwargs):
    if created:
        purchase_order = PurchaseOrder.objects.create(
            supplier=instance.supplier,
            total_amount=instance.purchase_price * instance.quantity,
        )
        purchase_order.save()

        PurchaseOrderItem.objects.create(
            product=instance,
            purchase_order=purchase_order,
            quantity=instance.quantity,
            purchase_price=instance.purchase_price,
        )
    else:
        try:
            old_quantity = Product.objects.get(pk=instance.pk).quantity
        except Product.DoesNotExist:
            old_quantity = None

        if old_quantity is not None and old_quantity < instance.quantity:
            if old_quantity != instance.quantity:
                new_quantity = instance.quantity - old_quantity
                purchase_order = PurchaseOrder.objects.create(
                    supplier=instance.supplier,
                    total_amount=instance.purchase_price * new_quantity,
                )

                PurchaseOrderItem.objects.create(
                    product=instance,
                    purchase_order=purchase_order,
                    quantity=new_quantity,
                    purchase_price=instance.purchase_price,
                )