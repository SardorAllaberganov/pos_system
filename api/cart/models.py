from django.db import models
from decimal import Decimal
from api.product.models import Product
from api.product.models import Product
from api.customer.models import Customer

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Cart: {self.id} - {self.customer}'

    @property
    def get_total_price(self):
        return sum(item.get_total_price for item in self.cart_items.all())

    @property
    def get_total_items(self):
        return sum(item.quantity for item in self.cart_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Cart ({self.cart.id})"

    @property
    def get_total_price(self):
        return Decimal(self.quantity) * Decimal(self.selling_price)
