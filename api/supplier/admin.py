from django.contrib import admin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum

from api.supplier.models import Supplier, PurchaseOrder, PurchaseOrderItem, SupplierPayment

admin.site.register(Supplier)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'order_date', 'total_amount', 'status')
    search_fields = ('supplier__name',)
    list_filter = ('status',)


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_order', 'product', 'quantity', 'purchase_price', 'total_price')
    readonly_fields = ['total_price']


from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SupplierPaymentForm(forms.ModelForm):
    class Meta:
        model = SupplierPayment
        fields = '__all__'

    def clean_amount(self):
        # Get the amount from the cleaned data
        amount = self.cleaned_data.get('amount')

        # Get the related purchase order
        purchase_order = self.cleaned_data.get('purchase_order')

        if purchase_order:
            total_amount = purchase_order.total_amount
            paid_amount = purchase_order.payments.aggregate(total=Sum('amount'))['total'] or 0
            due_amount = total_amount - (paid_amount + amount)

            if due_amount < 0:
                # raise ValidationError(_("The due amount cannot be negative. Check the payment amount."))
                self.add_error('amount',
                               f"The due amount cannot be negative. Check the payment amount. The due amount is {total_amount - paid_amount}")

        return amount


@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'purchase_order', 'amount', 'due_amount_display', 'payment_date', 'payment_method')
    list_filter = ('payment_method',)
    readonly_fields = ('due_amount_display',)


    def due_amount_display(self, obj):
        # Calculate the due amount for the related PurchaseOrder
        total_amount = obj.purchase_order.total_amount
        paid_amount = obj.purchase_order.payments.aggregate(total=Sum('amount'))['total'] or 0
        due_amount = total_amount - paid_amount
        return due_amount

    due_amount_display.short_description = 'Due Amount'

    form = SupplierPaymentForm

    def formfield_for_foreignkey(self, db_field, request, obj=None, **kwargs):
        if db_field.name == "purchase_order":
            kwargs["queryset"] = PurchaseOrder.objects.filter(status='pending')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
