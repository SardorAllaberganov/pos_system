from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.supplier.models import SupplierPayment
from django.db.models import Sum


@receiver(post_save, sender=SupplierPayment)
def update_due_amount_and_order_status(sender, instance, created, **kwargs):
    if created:
        purchase_order = instance.purchase_order
        total_amount = instance.purchase_order.total_amount
        paid_amount = instance.purchase_order.payments.aggregate(total=Sum('amount'))['total'] or 0

        due_amount = total_amount - paid_amount

        purchase_order.due_amount = due_amount

        if purchase_order.due_amount == 0:
            instance.purchase_order.status = 'approved'

        if purchase_order.due_amount < 0:
            raise ValidationError(
                _(f"The due amount cannot be negative. Check the payment amount. The due amount is {due_amount}"))

        purchase_order.save()
