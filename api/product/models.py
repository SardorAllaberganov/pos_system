import os.path

from django.db import models
from api.user.models import Account
from api.category.models import SubCategory
from api.supplier.models import Supplier
from django.dispatch import receiver
from django.db.models.signals import pre_save

class Product(models.Model):
    name = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100)
    sku = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subcategory = models.ForeignKey(SubCategory, related_name="products", on_delete=models.CASCADE)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, related_name="products", on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete_product_image(self, instance, **kwargs):
        if instance.image:
            instance.image.delete(False)

    def __str__(self):
        return self.name

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
