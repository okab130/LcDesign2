import requests
import logging
from datetime import datetime
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.db import transaction
from .models import LcShipmentRequest, LcShipmentRequestDetail
from .serializers import LcShipmentRequestSerializer

logger = logging.getLogger(__name__)


class LcShipmentRequestViewSet(viewsets.ModelViewSet):
    """出庫依頼のCRUD操作"""
    queryset = LcShipmentRequest.objects.all()
    serializer_class = LcShipmentRequestSerializer
    permission_classes = [AllowAny]  # 開発テスト環境では認証なし
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['request_status', 'base_code', 'delivery_date', 'request_date']
    search_fields = ['request_id', 'base_code__base_name']
    ordering_fields = ['request_date', 'delivery_date', 'created_at']
    ordering = ['-request_date', '-created_at']
    
    def get_queryset(self):
        """ユーザー権限に応じたクエリセットを返す"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # 開発テスト環境では認証チェックをスキップ
        if not user.is_authenticated:
            return queryset
        
        if user.user_type == 'BASE_STAFF':
            return queryset.filter(base_code=user.base_code)
        
        return queryset
    
    def perform_create(self, serializer):
        """出庫依頼作成時に依頼者を設定"""
        # 開発テスト環境では認証チェックをスキップ
        if self.request.user.is_authenticated:
            serializer.save(requested_by=self.request.user)
        else:
            serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """削除（送信済み・エラーは削除不可）"""
        instance = self.get_object()
        if instance.request_status != 'CREATED':
            return Response(
                {'error': '作成済の依頼のみ削除できます。'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def send_to_lc(self, request):
        """選択した出庫依頼をLC自動倉庫へ送信"""
        request_ids = request.data.get('request_ids', [])
        
        if not request_ids:
            return Response(
                {'error': '送信する出庫依頼を選択してください。'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        requests_to_send = LcShipmentRequest.objects.filter(
            request_id__in=request_ids,
            request_status='CREATED'
        )
        
        if not requests_to_send.exists():
            return Response(
                {'error': '送信可能な出庫依頼がありません。'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success_count = 0
        error_count = 0
        errors = []
        
        shipment_requests_data = []
        for req in requests_to_send:
            details = []
            for detail in req.details.all():
                details.append({
                    'product_code': detail.product_code.product_code,
                    'quantity': detail.requested_quantity
                })
            
            shipment_requests_data.append({
                'request_id': req.request_id,
                'base_code': req.base_code.base_code,
                'delivery_date': req.delivery_date.strftime('%Y-%m-%d'),
                'details': details
            })
        
        try:
            api_url = f"{settings.LC_WAREHOUSE_API_BASE_URL}/shipment-requests"
            headers = {
                'Authorization': f'Bearer {settings.LC_WAREHOUSE_API_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                api_url,
                json={'shipment_requests': shipment_requests_data},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                with transaction.atomic():
                    for req_result in result.get('results', []):
                        req_id = req_result.get('request_id')
                        is_success = req_result.get('success', False)
                        
                        try:
                            req_obj = LcShipmentRequest.objects.get(request_id=req_id)
                            if is_success:
                                req_obj.request_status = 'SENT'
                                req_obj.sent_by = request.user
                                req_obj.sent_at = datetime.now()
                                success_count += 1
                            else:
                                req_obj.request_status = 'ERROR'
                                error_count += 1
                                errors.append({
                                    'request_id': req_id,
                                    'error': req_result.get('error', '送信エラー')
                                })
                            req_obj.save()
                        except LcShipmentRequest.DoesNotExist:
                            pass
            else:
                for req in requests_to_send:
                    req.request_status = 'ERROR'
                    req.save()
                    error_count += 1
                
                logger.error(f'LC API送信エラー: {response.status_code} - {response.text}')
                return Response(
                    {'error': f'LC自動倉庫APIへの送信に失敗しました。ステータス: {response.status_code}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except requests.exceptions.Timeout:
            logger.error('LC API送信タイムアウト')
            return Response(
                {'error': 'LC自動倉庫APIへの接続がタイムアウトしました。'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except Exception as e:
            logger.error(f'LC API送信エラー: {str(e)}')
            return Response(
                {'error': f'LC自動倉庫APIへの送信中にエラーが発生しました: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': f'送信完了: {success_count}件成功, {error_count}件失敗',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def get_inventory(self, request):
        """LC自動倉庫から在庫情報を取得"""
        try:
            api_url = f"{settings.LC_WAREHOUSE_API_BASE_URL}/inventory"
            headers = {
                'Authorization': f'Bearer {settings.LC_WAREHOUSE_API_TOKEN}'
            }
            
            response = requests.get(api_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                logger.error(f'LC在庫API取得エラー: {response.status_code} - {response.text}')
                return Response(
                    {'error': f'在庫情報の取得に失敗しました。ステータス: {response.status_code}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except requests.exceptions.Timeout:
            logger.error('LC在庫API取得タイムアウト')
            return Response(
                {'error': 'LC自動倉庫APIへの接続がタイムアウトしました。'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except Exception as e:
            logger.error(f'LC在庫API取得エラー: {str(e)}')
            return Response(
                {'error': f'在庫情報の取得中にエラーが発生しました: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
