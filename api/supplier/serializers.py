from rest_framework import serializers

from api.supplier.models import Supplier, SupplierPayment, PurchaseOrder


class SupplierSerializer(serializers.ModelSerializer):
    total_order_amount = serializers.SerializerMethodField()
    total_paid_amount = serializers.SerializerMethodField()
    total_due_amount = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = '__all__'

    def get_total_order_amount(self, obj):
        return obj.total_order_amount()

    def get_total_paid_amount(self, obj):
        return obj.total_paid_amount()

    def get_total_due_amount(self, obj):
        return obj.total_due_amount()


class SupplierPaymentSerializer(serializers.ModelSerializer):
    due_amount = serializers.ReadOnlyField(source='due_amount')

    class Meta:
        model = SupplierPayment
        fields = '__all__'
