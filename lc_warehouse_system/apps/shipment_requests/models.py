from django.db import models
from apps.delivery_bases.models import DeliveryBase
from apps.products.models import Product
from apps.users.models import User


class LcShipmentRequest(models.Model):
    """LC出庫依頼テーブル"""
    
    STATUS_CHOICES = [
        ('CREATED', '作成済'),
        ('SENT', '送信済'),
        ('ERROR', 'エラー'),
    ]
    
    request_id = models.CharField(
        '出庫依頼ID',
        max_length=30,
        primary_key=True,
        help_text='出庫依頼を一意に識別するID'
    )
    base_code = models.ForeignKey(
        DeliveryBase,
        on_delete=models.PROTECT,
        verbose_name='配送拠点コード',
        db_column='base_code',
        to_field='base_code',
        help_text='配送先の拠点'
    )
    request_date = models.DateField(
        '依頼登録日',
        help_text='出庫依頼を登録した日付'
    )
    delivery_date = models.DateField(
        '配送予定日',
        help_text='配送拠点への配送予定日（=出庫日）。登録日の翌営業日（土日除く）を自動設定'
    )
    request_status = models.CharField(
        '依頼ステータス',
        max_length=20,
        choices=STATUS_CHOICES,
        default='CREATED',
        help_text='依頼の状態（作成済、送信済、エラー）。送信完了=完了'
    )
    total_quantity = models.IntegerField(
        '合計数量',
        default=0,
        help_text='依頼全体の合計ケース数'
    )
    note = models.TextField(
        '備考',
        blank=True,
        null=True,
        help_text='特記事項'
    )
    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='requested_shipments',
        verbose_name='依頼者',
        db_column='requested_by',
        to_field='user_id',
        null=True,
        blank=True,
        help_text='依頼を作成したユーザーID（開発テスト環境ではオプション）'
    )
    requested_at = models.DateTimeField(
        '依頼作成日時',
        auto_now_add=True,
        help_text='依頼作成日時'
    )
    sent_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sent_shipments',
        verbose_name='送信者',
        db_column='sent_by',
        to_field='user_id',
        null=True,
        blank=True,
        help_text='送信したLC倉庫担当のユーザーID'
    )
    sent_at = models.DateTimeField(
        '送信日時',
        null=True,
        blank=True,
        help_text='LC倉庫への送信日時'
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'lc_shipment_request'
        verbose_name = 'LC出庫依頼'
        verbose_name_plural = 'LC出庫依頼'
        ordering = ['-request_date', '-created_at']
        indexes = [
            models.Index(fields=['request_status'], name='idx_request_status'),
            models.Index(fields=['base_code', 'delivery_date'], name='idx_request_base_date'),
            models.Index(fields=['request_date'], name='idx_request_date'),
        ]
    
    def __str__(self):
        return f'{self.request_id} - {self.base_code} ({self.delivery_date})'


class LcShipmentRequestDetail(models.Model):
    """LC出庫依頼明細テーブル"""
    
    detail_id = models.BigAutoField(
        '明細ID',
        primary_key=True,
        help_text='明細を一意に識別するID'
    )
    request_id = models.ForeignKey(
        LcShipmentRequest,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='出庫依頼ID',
        db_column='request_id',
        to_field='request_id',
        help_text='親の出庫依頼'
    )
    line_number = models.IntegerField(
        '明細行番号',
        help_text='依頼内での明細順序'
    )
    product_code = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='商品コード',
        db_column='product_code',
        to_field='product_code',
        help_text='出庫する商品'
    )
    requested_quantity = models.IntegerField(
        '依頼数量',
        help_text='出庫を依頼するケース数。商品マスタのパレット積載ケース数の倍数であること'
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = 'lc_shipment_request_detail'
        verbose_name = 'LC出庫依頼明細'
        verbose_name_plural = 'LC出庫依頼明細'
        ordering = ['request_id', 'line_number']
        indexes = [
            models.Index(fields=['request_id', 'line_number'], name='idx_detail_request'),
        ]
        unique_together = [['request_id', 'line_number']]
    
    def __str__(self):
        return f'{self.request_id} - Line {self.line_number}'
