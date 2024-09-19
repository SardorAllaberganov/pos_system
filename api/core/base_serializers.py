from rest_framework import serializers
from django.utils import timezone

class BaseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        for field in ['created_at', 'updated_at', 'order_date']:
            if field in representation and isinstance(representation[field], str):
                try:
                    local_time = timezone.localtime(getattr(instance, field))
                    representation[field] = local_time.strftime('%d-%m-%Y %H:%M:%S')
                except AttributeError:
                    pass

        return representation
