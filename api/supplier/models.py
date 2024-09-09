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
        return f"Order {self.id} - {self.supplier.name}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE, related_name='purchase_orders_item')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        Product = apps.get_model('product', 'Product')
        product_name = Product.objects.get(id=self.product.id).name
        return f"{product_name} - {self.quantity} - {self.price}"


class SupplierPayment(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50,
                                      choices=[('cash', 'Cash'), ('card', 'Card'), ('bank_transfer', 'Bank Transfer')])

    def save(self, *args, **kwargs):
        total_amount = self.purchase_order.total_amount
        paid_amount = self.purchase_order.payments.aggregate(total_paid=Sum('amount'))['total_paid'] or 0
        self.due_amount = total_amount - (paid_amount + self.amount)
        if self.due_amount <= 0:
            if self.due_amount <= 0:
                self.purchase_order.status = 'approved'

        super().save(*args, **kwargs)
        if self.due_amount == 0:
            self.purchase_order.save()

    def __str__(self):
        return f"{self.amount} - {self.purchase_order_id}"
