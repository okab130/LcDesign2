from django.db import models


class DeliveryBase(models.Model):
    """配送拠点マスタ"""
    base_code = models.CharField(
        '拠点コード',
        max_length=10,
        primary_key=True,
        help_text='拠点を一意に識別するコード（30拠点）'
    )
    base_name = models.CharField(
        '拠点名',
        max_length=100,
        help_text='拠点の名称'
    )
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        db_table = 'delivery_base'
        verbose_name = '配送拠点'
        verbose_name_plural = '配送拠点'
        ordering = ['base_code']

    def __str__(self):
        return f'{self.base_code} - {self.base_name}'
