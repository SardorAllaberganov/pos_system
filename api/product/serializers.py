import os.path

from rest_framework import serializers
from .models import Product
from api.core.base_serializers import BaseSerializer
from api.user.models import Account
from api.supplier.models import Supplier
from api.category.models import SubCategory


class CustomSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name']


class CustomCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'name', 'email')


class ProductSerializer(BaseSerializer):
    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())
    creator = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    category = serializers.SerializerMethodField("get_category")

    @staticmethod
    def get_category(obj):
        return (
            {
                "id": obj.subcategory.category.id,
                "name": obj.subcategory.category.name,
            } if obj.subcategory and obj.subcategory.category else None)

    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['supplier'] = CustomSupplierSerializer(instance.supplier).data
        representation['category'] = self.get_category(obj=instance)
        representation['creator'] = CustomCreatorSerializer(instance.creator).data
        representation['subcategory'] = {
            'id': instance.subcategory.id,
            'name': instance.subcategory.name,
        }
        return representation
