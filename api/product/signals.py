from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from api.product.models import Product
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
