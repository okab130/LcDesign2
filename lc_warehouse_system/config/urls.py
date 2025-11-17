from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT認証エンドポイント（開発テスト環境では未使用）
    # path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/delivery-bases/', include('apps.delivery_bases.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/shipment-requests/', include('apps.shipment_requests.urls')),
    path('api/v1/shipment-results/', include('apps.shipment_results.urls')),
]
