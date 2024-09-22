from rest_framework import serializers
from .models import Sale, SaleItem
from api.core.base_serializers import BaseSerializer

class SaleItemSerializer(BaseSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'quantity', 'selling_price', 'get_total_price']
        read_only_fields = ['selling_price']

class SaleSerializer(BaseSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    cashier_name = serializers.CharField(source='cashier.name', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'customer', 'items', 'cashier_name', 'total_amount', 'total_amount', 'created_at', 'updated_at',
                  'payment_status']
