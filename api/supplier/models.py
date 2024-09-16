from django.db import models
from django.apps import apps
from django.db.models import Sum


class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_person = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_order_amount(self):
        return self.purchase_orders.aggregate(total_amount=models.Sum('total_amount'))['total_amount'] or 0

    def total_paid_amount(self):
        return self.payments.aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0

    def total_due_amount(self):
        return self.total_order_amount() - self.total_paid_amount()

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved')],
                              default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.supplier.name} - {self.supplier_id}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE, related_name='purchase_orders_item')
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.purchase_price

    def __str__(self):
        Product = apps.get_model('product', 'Product')
        product_name = Product.objects.get(id=self.product.id).name
        return f"{product_name} - {self.quantity} - {self.purchase_price}"


class SupplierPayment(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50,
                                      choices=[('cash', 'Cash'), ('card', 'Card'), ('bank_transfer', 'Bank Transfer')])

    def __str__(self):
        return f"{self.amount} - {self.purchase_order_id}"
