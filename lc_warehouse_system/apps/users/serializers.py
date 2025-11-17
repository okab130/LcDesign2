from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """ユーザーマスタシリアライザー"""
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'password',
            'user_name',
            'user_type',
            'base_code',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """ユーザー作成"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        """ユーザー更新"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
    def validate(self, data):
        """バリデーション"""
        user_type = data.get('user_type')
        base_code = data.get('base_code')
        
        if user_type == 'BASE_STAFF' and not base_code:
            raise serializers.ValidationError({
                'base_code': '拠点倉庫担当は所属拠点の指定が必要です。'
            })
        
        if user_type in ['LC_STAFF', 'ADMIN'] and base_code:
            raise serializers.ValidationError({
                'base_code': 'LC倉庫担当・管理者は所属拠点を指定できません。'
            })
        
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """パスワード変更シリアライザー"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
