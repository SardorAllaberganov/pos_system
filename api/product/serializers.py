import os.path

from rest_framework import serializers
from .models import Product
from api.category.serializers import SubcategorySerializer, CategorySerializer
from api.user.models import Account
from api.supplier.models import Supplier


class ProductSerializer(serializers.ModelSerializer):
    subcategory = SubcategorySerializer()
    category = serializers.SerializerMethodField("get_category")

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

    @staticmethod
    def get_category(obj):
        return obj.subcategory.category.name if obj.subcategory and obj.subcategory.category else None

    class Meta:
        model = Product
        fields = '__all__'
