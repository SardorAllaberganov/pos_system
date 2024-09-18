from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        for field in ['created_at', 'updated_at', 'order_date']:
            if field in representation and isinstance(representation[field], str):
                try:
                    representation[field] = instance.__getattribute__(field).strftime('%d-%m-%Y %H:%M:%S')
                except AttributeError:
                    pass

        return representation
