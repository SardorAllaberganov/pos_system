import os.path

from django.db import models
from api.user.models import Account
from api.category.models import SubCategory
from api.supplier.models import Supplier, PurchaseOrder, PurchaseOrderItem
from django.dispatch import receiver
from django.db.models.signals import pre_save


def upload_location(instance, filename):
    file_path = "product_images/{name}-{filename}".format(
        name=str(instance.name), filename=filename
    )
    return file_path


class Product(models.Model):
    name = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100)
    unit_type = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subcategory = models.ForeignKey(SubCategory, related_name="products", on_delete=models.CASCADE)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, related_name="products", on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to=upload_location, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete_product_image(self, instance, **kwargs):
        if instance.image:
            instance.image.delete(False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        old_quantity = None
        if not is_new:
            try:
                old_quantity = Product.objects.get(pk=self.pk).quantity
            except Product.DoesNotExist:
                old_quantity = None

        super().save(*args, **kwargs)

        if is_new:
            purchase_order = PurchaseOrder.objects.create(
                supplier=self.supplier,
                total_amount=self.price * self.quantity,
            )
            purchase_order.save()

            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order,
                product=self,
                quantity=self.quantity,
                price=self.price
            )
            purchase_order.save()
        elif old_quantity is not None and self.quantity > old_quantity:
            if self.quantity != old_quantity:
                new_quantity = self.quantity - old_quantity
                purchase_order = PurchaseOrder.objects.create(
                    supplier=self.supplier,
                    total_amount=self.price * new_quantity
                )
                PurchaseOrderItem.objects.create(
                    purchase_order=purchase_order,
                    product=self,
                    quantity=new_quantity,
                    price=self.price
                )


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
