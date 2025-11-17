from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import User
from .serializers import UserSerializer, ChangePasswordSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ユーザーマスタのCRUD操作"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # 開発テスト環境では認証なし
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_type', 'is_active', 'base_code']
    search_fields = ['user_id', 'user_name']
    ordering_fields = ['user_id', 'user_name', 'created_at']
    ordering = ['user_id']

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """パスワード変更"""
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': '現在のパスワードが正しくありません。'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response(
                {'message': 'パスワードを変更しました。'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """現在ログイン中のユーザー情報を取得"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
