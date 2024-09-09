from django.contrib import admin

from api.supplier.models import Supplier, PurchaseOrder, PurchaseOrderItem, SupplierPayment

admin.site.register(Supplier)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'order_date', 'total_amount', 'status')
    search_fields = ('supplier__name',)
    list_filter = ('status',)


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_order', 'product', 'quantity', 'price', 'total_price')
    readonly_fields = ['total_price']


@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'purchase_order', 'amount', 'payment_date', 'payment_method')
    list_filter = ('payment_method',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "purchase_order":
            kwargs["queryset"] = PurchaseOrder.pending_orders.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
