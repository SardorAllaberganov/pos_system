from django.contrib import admin

from api.cart.models import Cart, CartItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "quantity", "selling_price", 'get_total_price')

@admin.register(Cart)
class CartsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Cart._meta.fields]
