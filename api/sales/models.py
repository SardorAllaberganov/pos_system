from django.db import models
from api.product.models import Product
from api.customer.models import Customer
from api.user.models import Account
from decimal import Decimal

class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cashier = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(max_length=10, choices=[('pending', "Pending"), ('completed', "Completed")],
                                      default='pending')

    def __str__(self):
        return f"Sale {self.id} by {self.customer.name}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def get_total_price(self):
        return Decimal(self.quantity) * Decimal(self.selling_price)
