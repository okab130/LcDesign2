from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """商品マスタシリアライザー"""
    
    class Meta:
        model = Product
        fields = [
            'product_code',
            'product_name',
            'pallet_case_quantity',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_pallet_case_quantity(self, value):
        """パレット積載ケース数のバリデーション"""
        if value <= 0:
            raise serializers.ValidationError('パレット積載ケース数は1以上である必要があります。')
        return value
