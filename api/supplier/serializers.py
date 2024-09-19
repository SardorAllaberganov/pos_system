from rest_framework import serializers

from api.supplier.models import Supplier, SupplierPayment, PurchaseOrder, PurchaseOrderItem
from api.product.models import Product
from api.core.base_serializers import BaseSerializer


class SupplierSerializer(BaseSerializer):
    total_order_amount = serializers.SerializerMethodField()
    total_paid_amount = serializers.SerializerMethodField()
    total_due_amount = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = '__all__'

    @staticmethod
    def get_total_order_amount(obj):
        return obj.total_order_amount()

    @staticmethod
    def get_total_paid_amount(self, obj):
        return obj.total_paid_amount()

    @staticmethod
    def get_total_due_amount(self, obj):
        return obj.total_due_amount()


class SupplierPaymentSerializer(BaseSerializer):
    due_amount = serializers.ReadOnlyField(source='due_amount')

    class Meta:
        model = SupplierPayment
        fields = '__all__'


class PurchaseOrderSerializer(BaseSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    class CustomSupplierSerializer(BaseSerializer):
        class Meta:
            model = Supplier
            fields = ['name']

    supplier = CustomSupplierSerializer()


class PurchaseOrderItemSerializer(BaseSerializer):
    total_amount = serializers.ReadOnlyField(source='total_price')

    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'

    class CustomProductSerializer(BaseSerializer):
        class Meta:
            model = Product
            fields = ['name']

    product = CustomProductSerializer()
