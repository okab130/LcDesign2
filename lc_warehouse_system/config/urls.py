from django.contrib import admin
from django.urls import path, include
from apps.users.views_web import (
    login_view, logout_view, top_view, inventory_view,
    shipment_request_list_view, shipment_request_register_view,
    shipment_request_detail_view, shipment_result_list_view
)

urlpatterns = [
    # フロントエンド画面
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('top/', top_view, name='top'),
    path('inventory/', inventory_view, name='inventory'),
    path('shipment-request/', shipment_request_list_view, name='shipment_request_list'),
    path('shipment-request/register/', shipment_request_register_view, name='shipment_request_register'),
    path('shipment-request/<str:request_id>/', shipment_request_detail_view, name='shipment_request_detail'),
    path('shipment-result/', shipment_result_list_view, name='shipment_result_list'),
    
    # 管理画面
    path('admin/', admin.site.urls),
    
    # API エンドポイント
    # JWT認証エンドポイント（開発テスト環境では未使用）
    # path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/delivery-bases/', include('apps.delivery_bases.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/shipment-requests/', include('apps.shipment_requests.urls')),
    path('api/v1/shipment-results/', include('apps.shipment_results.urls')),
]
