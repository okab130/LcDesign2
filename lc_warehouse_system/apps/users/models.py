from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from apps.delivery_bases.models import DeliveryBase


class UserManager(BaseUserManager):
    """カスタムユーザーマネージャー"""
    
    def create_user(self, user_id, password=None, **extra_fields):
        """通常ユーザーの作成"""
        if not user_id:
            raise ValueError('ユーザーIDは必須です')
        
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, user_id, password=None, **extra_fields):
        """スーパーユーザーの作成"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'ADMIN')
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('スーパーユーザーはis_staff=Trueである必要があります')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('スーパーユーザーはis_superuser=Trueである必要があります')
        
        return self.create_user(user_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """ユーザーマスタ"""
    
    USER_TYPE_CHOICES = [
        ('BASE_STAFF', '拠点倉庫担当'),
        ('LC_STAFF', 'LC倉庫担当'),
        ('ADMIN', '管理者'),
    ]
    
    user_id = models.CharField(
        'ユーザーID',
        max_length=50,
        primary_key=True,
        help_text='ログインIDとして使用'
    )
    user_name = models.CharField(
        'ユーザー名',
        max_length=100,
        help_text='ユーザーの氏名'
    )
    user_type = models.CharField(
        'ユーザー区分',
        max_length=20,
        choices=USER_TYPE_CHOICES,
        help_text='ユーザーの種類（拠点倉庫担当、LC倉庫担当、管理者）'
    )
    base_code = models.ForeignKey(
        DeliveryBase,
        on_delete=models.PROTECT,
        verbose_name='所属拠点コード',
        db_column='base_code',
        to_field='base_code',
        null=True,
        blank=True,
        help_text='所属する配送拠点（拠点倉庫担当のみ。LC倉庫担当・管理者はNULL）'
    )
    is_active = models.BooleanField(
        '有効フラグ',
        default=True,
        help_text='利用可否'
    )
    is_staff = models.BooleanField('スタッフ権限', default=False)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['user_name', 'user_type']
    
    class Meta:
        db_table = 'user'
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        ordering = ['user_id']
        indexes = [
            models.Index(fields=['user_type'], name='idx_user_type'),
            models.Index(fields=['base_code'], name='idx_user_base'),
        ]
    
    def __str__(self):
        return f'{self.user_id} - {self.user_name}'
    
    def has_base_permission(self, base_code):
        """指定拠点へのアクセス権限チェック"""
        if self.user_type in ['LC_STAFF', 'ADMIN']:
            return True
        return str(self.base_code_id) == str(base_code)
