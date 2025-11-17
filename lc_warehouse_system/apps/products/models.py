from django.db import models


class Product(models.Model):
    """商品マスタ"""
    product_code = models.CharField(
        '商品コード',
        max_length=20,
        primary_key=True,
        help_text='商品を一意に識別するコード'
    )
    product_name = models.CharField(
        '商品名',
        max_length=100,
        help_text='商品の名称（例：アルコーラ、アルコーヒー）'
    )
    pallet_case_quantity = models.IntegerField(
        'パレット積載ケース数',
        help_text='1パレットあたりの標準ケース数（出庫依頼の単位チェックに使用）'
    )
    is_active = models.BooleanField(
        '有効フラグ',
        default=True,
        help_text='取扱中か否か'
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'product'
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['product_code']

    def __str__(self):
        return f'{self.product_code} - {self.product_name}'
