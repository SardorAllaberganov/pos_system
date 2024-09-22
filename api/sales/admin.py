from django.contrib import admin

from api.sales.models import Sale, SaleItem

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', "customer", 'cashier', 'total_amount', 'payment_status')

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("id", 'sale', 'product', 'quantity', 'selling_price')
