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
    payment_type = models.CharField(max_length=15, choices=[('cash', "Cash"), ("card", "Card"),
                                                            ('loyalty_points', "Loyalty Points")], default="cash")
    loyalty_points_used = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Sale {self.id} by {self.customer.name}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def get_total_price(self):
        return Decimal(self.quantity) * Decimal(self.selling_price)

    def __str__(self):
        return (
            f"Sale {self.id} |  Product: {self.product.name} | Quantity: {self.quantity} | Price: {self.selling_price}"
            f" | Total: {self.get_total_price}")

class Receipt(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cashier = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=15)

    def __str__(self):
        return f"Receipt {self.receipt_number} for Sale {self.sale.id}"
