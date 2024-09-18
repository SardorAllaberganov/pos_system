from rest_framework import serializers
from api.core.base_serializers import BaseSerializer
from api.customer.models import Customer


class CustomerSerializer(BaseSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
