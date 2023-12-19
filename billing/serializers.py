from rest_framework import serializers
from .models import LocalGovernmentArea, State


class LocalGovernmentAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalGovernmentArea
        fields = ['id', 'name']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name']


class BillingPriceSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

