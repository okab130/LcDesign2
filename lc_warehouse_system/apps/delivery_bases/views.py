import csv
import os
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from .models import DeliveryBase
from .serializers import DeliveryBaseSerializer


class DeliveryBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """配送拠点マスタの参照（CSV取り込み機能付き）"""
    queryset = DeliveryBase.objects.all()
    serializer_class = DeliveryBaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['base_code', 'base_name']
    ordering_fields = ['base_code', 'base_name']
    ordering = ['base_code']

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """CSVファイルから配送拠点マスタを取り込み"""
        try:
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response(
                    {'error': 'CSVファイルが指定されていません。'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not csv_file.name.endswith('.csv'):
                return Response(
                    {'error': 'CSVファイル形式でアップロードしてください。'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            DeliveryBase.objects.all().delete()

            imported_count = 0
            for row in reader:
                DeliveryBase.objects.create(
                    base_code=row['拠点コード'],
                    base_name=row['拠点名']
                )
                imported_count += 1

            return Response(
                {'message': f'{imported_count}件の配送拠点を取り込みました。'},
                status=status.HTTP_200_OK
            )

        except KeyError as e:
            return Response(
                {'error': f'CSVファイルに必須カラムがありません: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'CSV取り込み中にエラーが発生しました: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
