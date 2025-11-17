from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LcShipmentRequestViewSet

router = DefaultRouter()
router.register(r'', LcShipmentRequestViewSet, basename='shipment-request')

urlpatterns = [
    path('', include(router.urls)),
]
