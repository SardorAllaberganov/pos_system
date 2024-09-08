import os.path

from rest_framework import serializers
from .models import Product
from api.category.serializers import SubcategorySerializer
from api.user.models import Account
from api.supplier.models import Supplier

class ProductSerializer(serializers.ModelSerializer):
    subcategory = SubcategorySerializer()

    class CustomSupplierSerializer(serializers.ModelSerializer):
        class Meta:
            model = Supplier
            fields = ['id', 'name']

    class CustomCreatorSerializer(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = ('id', 'username', 'name', 'email')

    creator = CustomCreatorSerializer()
    supplier = CustomSupplierSerializer()

    class Meta:
        model = Product
        fields = '__all__'
