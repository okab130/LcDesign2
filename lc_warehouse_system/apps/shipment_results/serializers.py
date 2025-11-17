from rest_framework import serializers
from .models import LcShipmentResult


class LcShipmentResultSerializer(serializers.ModelSerializer):
    """出庫実績シリアライザー"""
    base_name = serializers.CharField(source='base_code.base_name', read_only=True)
    
    class Meta:
        model = LcShipmentResult
        fields = [
            'result_id',
            'request_id',
            'pallet_id',
            'product_code',
            'quantity',
            'shipment_type',
            'shipment_datetime',
            'base_code',
            'base_name',
            'location_code',
            'factory_code',
            'line_code',
            'production_number',
            'production_date',
            'expiry_date',
            'received_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['received_at', 'created_at', 'updated_at']


class LcShipmentResultWebhookSerializer(serializers.Serializer):
    """Webhook受信用シリアライザー"""
    results = serializers.ListField(child=serializers.DictField())
