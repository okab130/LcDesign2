from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryBaseViewSet

router = DefaultRouter()
router.register(r'', DeliveryBaseViewSet, basename='delivery-base')

urlpatterns = [
    path('', include(router.urls)),
]
