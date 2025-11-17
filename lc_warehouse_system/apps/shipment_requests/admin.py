from django.contrib import admin
from .models import LcShipmentRequest, LcShipmentRequestDetail


class LcShipmentRequestDetailInline(admin.TabularInline):
    model = LcShipmentRequestDetail
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LcShipmentRequest)
class LcShipmentRequestAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'base_code', 'delivery_date', 'request_status', 'total_quantity', 'requested_by', 'sent_at']
    list_filter = ['request_status', 'delivery_date', 'created_at']
    search_fields = ['request_id', 'base_code__base_name']
    readonly_fields = ['request_id', 'requested_at', 'sent_at', 'created_at', 'updated_at']
    inlines = [LcShipmentRequestDetailInline]
    
    fieldsets = (
        ('基本情報', {'fields': ('request_id', 'base_code', 'request_date', 'delivery_date', 'request_status')}),
        ('数量・備考', {'fields': ('total_quantity', 'note')}),
        ('依頼・送信情報', {'fields': ('requested_by', 'requested_at', 'sent_by', 'sent_at')}),
        ('日時情報', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(LcShipmentRequestDetail)
class LcShipmentRequestDetailAdmin(admin.ModelAdmin):
    list_display = ['detail_id', 'request_id', 'line_number', 'product_code', 'requested_quantity']
    list_filter = ['created_at']
    search_fields = ['request_id__request_id', 'product_code__product_name']
    readonly_fields = ['created_at', 'updated_at']
