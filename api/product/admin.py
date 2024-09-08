from django.contrib import admin
from api.product.models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]
    list_filter = ("name", "price", "sku")
    search_fields = ("name", "price", "sku")
    empty_value_display = "N/A"
