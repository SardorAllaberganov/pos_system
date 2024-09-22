from rest_framework import serializers
from api.core.base_serializers import BaseSerializer
from .models import Cart, CartItem

class CartSerializer(BaseSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'customer', 'created_at', 'updated_at', 'is_active', 'get_total_price', 'get_total_items']

class CartItemSerializer(BaseSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'quantity', 'selling_price', 'get_total_price']
        read_only_fields = ['get_total_price']
