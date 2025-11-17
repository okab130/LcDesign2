from django.contrib import admin
from .models import LcShipmentResult


@admin.register(LcShipmentResult)
class LcShipmentResultAdmin(admin.ModelAdmin):
    list_display = [
        'result_id',
        'pallet_id',
        'product_code',
        'quantity',
        'shipment_type',
        'shipment_datetime',
        'base_code',
        'expiry_date'
    ]
    list_filter = ['shipment_type', 'shipment_datetime', 'base_code', 'expiry_date']
    search_fields = [
        'result_id',
        'pallet_id',
        'product_code',
        'production_number',
        'factory_code',
        'line_code'
    ]
    readonly_fields = ['received_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': (
                'result_id',
                'request_id',
                'pallet_id',
                'product_code',
                'quantity',
                'shipment_type'
            )
        }),
        ('出庫情報', {
            'fields': (
                'shipment_datetime',
                'base_code',
                'location_code'
            )
        }),
        ('製造情報', {
            'fields': (
                'factory_code',
                'line_code',
                'production_number',
                'production_date',
                'expiry_date'
            )
        }),
        ('日時情報', {
            'fields': (
                'received_at',
                'created_at',
                'updated_at'
            )
        }),
    )
