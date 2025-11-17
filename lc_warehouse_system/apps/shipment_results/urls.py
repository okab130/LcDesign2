from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LcShipmentResultViewSet

router = DefaultRouter()
router.register(r'', LcShipmentResultViewSet, basename='shipment-result')

urlpatterns = [
    path('', include(router.urls)),
]
