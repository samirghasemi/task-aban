# orders/serializers.py

from rest_framework import serializers
from .models import Cryptocurrency

class OrderSerializer(serializers.Serializer):
    cryptocurrency = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=12, decimal_places=4)

    def validate(self, data):
        try:
            crypto = Cryptocurrency.objects.get(name=data['cryptocurrency'])
        except Cryptocurrency.DoesNotExist:
            raise serializers.ValidationError("Cryptocurrency does not exist.")
        data['cryptocurrency_obj'] = crypto
        return data
