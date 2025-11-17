from datetime import datetime, timedelta
from rest_framework import serializers
from .models import LcShipmentRequest, LcShipmentRequestDetail
from apps.products.models import Product
from apps.delivery_bases.models import DeliveryBase


class LcShipmentRequestDetailSerializer(serializers.ModelSerializer):
    """出庫依頼明細シリアライザー"""
    product_code = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        pk_field=serializers.CharField()
    )
    product_name = serializers.CharField(source='product_code.product_name', read_only=True)
    pallet_case_quantity = serializers.IntegerField(source='product_code.pallet_case_quantity', read_only=True)
    
    class Meta:
        model = LcShipmentRequestDetail
        fields = [
            'detail_id',
            'line_number',
            'product_code',
            'product_name',
            'pallet_case_quantity',
            'requested_quantity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['detail_id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """明細のバリデーション"""
        product = data.get('product_code')
        requested_quantity = data.get('requested_quantity')
        
        if requested_quantity <= 0:
            raise serializers.ValidationError({
                'requested_quantity': '依頼数量は1以上である必要があります。'
            })
        
        # パレット積載数チェックは緩和（開発テスト環境）
        # if requested_quantity % product.pallet_case_quantity != 0:
        #     raise serializers.ValidationError({
        #         'requested_quantity': f'依頼数量はパレット積載ケース数（{product.pallet_case_quantity}）の倍数である必要があります。'
        #     })
        
        return data


class LcShipmentRequestSerializer(serializers.ModelSerializer):
    """出庫依頼シリアライザー"""
    details = LcShipmentRequestDetailSerializer(many=True)
    base_code = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryBase.objects.all(),
        pk_field=serializers.CharField()
    )
    base_name = serializers.CharField(source='base_code.base_name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.user_name', read_only=True, allow_null=True)
    sent_by_name = serializers.CharField(source='sent_by.user_name', read_only=True, allow_null=True)
    
    class Meta:
        model = LcShipmentRequest
        fields = [
            'request_id',
            'base_code',
            'base_name',
            'request_date',
            'delivery_date',
            'request_status',
            'total_quantity',
            'note',
            'requested_by',
            'requested_by_name',
            'requested_at',
            'sent_by',
            'sent_by_name',
            'sent_at',
            'details',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'request_id', 'request_date', 'request_status', 
            'requested_by', 'requested_at', 'sent_by', 'sent_at', 
            'created_at', 'updated_at'
        ]
    
    def calculate_next_business_day(self, date):
        """翌営業日を計算（土日のみ除外）"""
        next_day = date + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        return next_day
    
    def create(self, validated_data):
        """出庫依頼の作成"""
        details_data = validated_data.pop('details')
        
        # request_dateを自動設定
        request_date = datetime.now().date()
        validated_data['request_date'] = request_date
        
        # delivery_dateが指定されていない場合は翌営業日
        if 'delivery_date' not in validated_data or not validated_data['delivery_date']:
            validated_data['delivery_date'] = self.calculate_next_business_day(request_date)
        
        # request_idを自動生成
        base_code = validated_data['base_code'].base_code
        request_id = f"REQ{datetime.now().strftime('%Y%m%d%H%M%S')}{base_code}"
        validated_data['request_id'] = request_id
        
        # total_quantityを計算
        total_quantity = sum(detail['requested_quantity'] for detail in details_data)
        validated_data['total_quantity'] = total_quantity
        
        # requested_byは開発テスト環境ではオプション
        # 本番環境ではViewでセット
        
        request = LcShipmentRequest.objects.create(**validated_data)
        
        for index, detail_data in enumerate(details_data, start=1):
            LcShipmentRequestDetail.objects.create(
                request_id=request,
                line_number=detail_data.get('line_number', index),
                product_code=detail_data['product_code'],
                requested_quantity=detail_data['requested_quantity']
            )
        
        return request
    
    def update(self, instance, validated_data):
        """出庫依頼の更新"""
        details_data = validated_data.pop('details', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if details_data is not None:
            instance.details.all().delete()
            
            total_quantity = sum(detail['requested_quantity'] for detail in details_data)
            instance.total_quantity = total_quantity
            
            for index, detail_data in enumerate(details_data, start=1):
                LcShipmentRequestDetail.objects.create(
                    request_id=instance,
                    line_number=index,
                    **detail_data
                )
        
        instance.save()
        return instance
