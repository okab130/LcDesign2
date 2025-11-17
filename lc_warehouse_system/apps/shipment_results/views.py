import logging
from datetime import datetime
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import LcShipmentResult
from .serializers import LcShipmentResultSerializer, LcShipmentResultWebhookSerializer

logger = logging.getLogger(__name__)


class LcShipmentResultViewSet(viewsets.ReadOnlyModelViewSet):
    """出庫実績の参照"""
    queryset = LcShipmentResult.objects.all()
    serializer_class = LcShipmentResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'shipment_type',
        'base_code',
        'product_code',
        'pallet_id',
        'request_id',
        'production_date',
        'expiry_date',
    ]
    search_fields = [
        'result_id',
        'pallet_id',
        'product_code',
        'production_number',
        'factory_code',
        'line_code',
    ]
    ordering_fields = ['shipment_datetime', 'received_at', 'expiry_date']
    ordering = ['-shipment_datetime']
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def webhook(self, request):
        """LC自動倉庫からの出庫実績Webhook受信"""
        try:
            serializer = LcShipmentResultWebhookSerializer(data=request.data)
            
            if not serializer.is_valid():
                logger.error(f'Webhook受信データ検証エラー: {serializer.errors}')
                return Response(
                    {'error': 'データ検証エラー', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results_data = serializer.validated_data.get('results', [])
            created_count = 0
            
            for result_data in results_data:
                try:
                    shipment_datetime_str = result_data.get('shipment_datetime')
                    shipment_datetime = datetime.fromisoformat(shipment_datetime_str.replace('Z', '+00:00'))
                    
                    production_date = None
                    if result_data.get('production_date'):
                        production_date = datetime.strptime(result_data['production_date'], '%Y-%m-%d').date()
                    
                    expiry_date = None
                    if result_data.get('expiry_date'):
                        expiry_date = datetime.strptime(result_data['expiry_date'], '%Y-%m-%d').date()
                    
                    LcShipmentResult.objects.create(
                        result_id=result_data['result_id'],
                        request_id_id=result_data.get('request_id'),
                        pallet_id=result_data['pallet_id'],
                        product_code=result_data['product_code'],
                        quantity=result_data['quantity'],
                        shipment_type=result_data.get('shipment_type', 'AUTO'),
                        shipment_datetime=shipment_datetime,
                        base_code_id=result_data.get('base_code'),
                        location_code=result_data.get('location_code'),
                        factory_code=result_data.get('factory_code'),
                        line_code=result_data.get('line_code'),
                        production_number=result_data.get('production_number'),
                        production_date=production_date,
                        expiry_date=expiry_date,
                    )
                    created_count += 1
                    
                except Exception as e:
                    logger.error(f'出庫実績作成エラー: {str(e)} - データ: {result_data}')
                    continue
            
            logger.info(f'出庫実績Webhook受信: {created_count}件作成')
            
            return Response(
                {
                    'message': f'{created_count}件の出庫実績を受信しました。',
                    'created_count': created_count
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f'Webhook受信エラー: {str(e)}')
            return Response(
                {'error': f'出庫実績の受信中にエラーが発生しました: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
