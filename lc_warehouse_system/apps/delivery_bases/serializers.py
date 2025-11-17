from rest_framework import serializers
from .models import DeliveryBase


class DeliveryBaseSerializer(serializers.ModelSerializer):
    """配送拠点マスタシリアライザー"""
    
    class Meta:
        model = DeliveryBase
        fields = [
            'base_code',
            'base_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
