from django.db import models
from apps.delivery_bases.models import DeliveryBase
from apps.shipment_requests.models import LcShipmentRequest


class LcShipmentResult(models.Model):
    """LC出庫実績テーブル"""
    
    SHIPMENT_TYPE_CHOICES = [
        ('AUTO', '自動'),
        ('MANUAL', '手動'),
    ]
    
    result_id = models.CharField(
        '出庫実績ID',
        max_length=30,
        primary_key=True,
        help_text='出庫実績を一意に識別するID'
    )
    request_id = models.ForeignKey(
        LcShipmentRequest,
        on_delete=models.PROTECT,
        verbose_name='出庫依頼ID',
        db_column='request_id',
        to_field='request_id',
        null=True,
        blank=True,
        help_text='元の出庫依頼（自動出庫の場合のみ紐付く。手動出庫はNULL）'
    )
    pallet_id = models.CharField(
        'パレットID',
        max_length=30,
        help_text='出庫されたパレット'
    )
    product_code = models.CharField(
        '商品コード',
        max_length=20,
        help_text='出庫された商品'
    )
    quantity = models.IntegerField(
        '出庫数量',
        help_text='実際に出庫されたケース数'
    )
    shipment_type = models.CharField(
        '出庫区分',
        max_length=20,
        choices=SHIPMENT_TYPE_CHOICES,
        help_text='出庫方法（自動、手動）。手動は緊急出庫・廃棄など'
    )
    shipment_datetime = models.DateTimeField(
        '出庫日時',
        help_text='LC倉庫から出庫された日時'
    )
    base_code = models.ForeignKey(
        DeliveryBase,
        on_delete=models.PROTECT,
        verbose_name='配送拠点コード',
        db_column='base_code',
        to_field='base_code',
        null=True,
        blank=True,
        help_text='配送先拠点'
    )
    location_code = models.CharField(
        '出庫元ロケーション',
        max_length=20,
        null=True,
        blank=True,
        help_text='倉庫内の出庫元位置'
    )
    factory_code = models.CharField(
        '製造工場コード',
        max_length=10,
        null=True,
        blank=True,
        help_text='製造工場（検索・表示用）'
    )
    line_code = models.CharField(
        '製造ラインコード',
        max_length=20,
        null=True,
        blank=True,
        help_text='製造ライン（検索・表示用）'
    )
    production_number = models.CharField(
        '製造番号',
        max_length=30,
        null=True,
        blank=True,
        help_text='製造ロット番号'
    )
    production_date = models.DateField(
        '製造年月日',
        null=True,
        blank=True,
        help_text='製造日'
    )
    expiry_date = models.DateField(
        '賞味期限',
        null=True,
        blank=True,
        help_text='賞味期限'
    )
    received_at = models.DateTimeField(
        '受信日時',
        auto_now_add=True,
        help_text='実績情報受信日時'
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'lc_shipment_result'
        verbose_name = 'LC出庫実績'
        verbose_name_plural = 'LC出庫実績'
        ordering = ['-shipment_datetime']
        indexes = [
            models.Index(fields=['request_id'], name='idx_result_request'),
            models.Index(fields=['pallet_id'], name='idx_result_pallet'),
            models.Index(fields=['shipment_datetime'], name='idx_result_shipment_date'),
            models.Index(fields=['base_code', 'shipment_datetime'], name='idx_result_base_date'),
            models.Index(fields=['product_code'], name='idx_result_product'),
            models.Index(fields=['expiry_date'], name='idx_result_expiry'),
        ]
    
    def __str__(self):
        return f'{self.result_id} - {self.pallet_id}'
