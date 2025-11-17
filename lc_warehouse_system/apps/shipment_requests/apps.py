from django.apps import AppConfig


class ShipmentRequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shipment_requests'
    verbose_name = '出庫依頼管理'
