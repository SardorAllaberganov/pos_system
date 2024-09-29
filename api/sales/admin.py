from django.contrib import admin

from api.sales.models import Sale, SaleItem, Receipt

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'id', "customer", 'cashier', 'total_amount', 'payment_status', 'payment_type', 'loyalty_points_used')

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    readonly_fields = ['get_total_price']
    list_display = ("id", 'sale', 'product', 'quantity', 'selling_price', 'get_total_price')

# admin.site.register(SaleItem)

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'created_at', 'cashier', 'customer', 'total_amount', 'payment_type')
