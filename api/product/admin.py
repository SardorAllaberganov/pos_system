from django.contrib import admin
from api.product.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]
    list_filter = ("name", "purchase_price", "selling_price", "unit_type")
    search_fields = ("name", "purchase_price", "selling_price", "unit_type")
    empty_value_display = "N/A"
