import os.path

from django.db import models
from api.user.models import Account
from api.category.models import SubCategory
from api.supplier.models import Supplier, PurchaseOrder, PurchaseOrderItem


def upload_location(instance, filename):
    file_path = "product_images/{name}-{filename}".format(
        name=str(instance.name), filename=filename
    )
    return file_path


class Product(models.Model):
    name = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, unique=True)
    unit_type = models.CharField(max_length=100)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    subcategory = models.ForeignKey(SubCategory, related_name="products", on_delete=models.CASCADE)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, related_name="products", on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to=upload_location, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
