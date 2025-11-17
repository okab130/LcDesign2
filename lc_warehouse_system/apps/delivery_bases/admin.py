from django.contrib import admin
from .models import DeliveryBase


@admin.register(DeliveryBase)
class DeliveryBaseAdmin(admin.ModelAdmin):
    list_display = ['base_code', 'base_name', 'created_at', 'updated_at']
    search_fields = ['base_code', 'base_name']
    readonly_fields = ['created_at', 'updated_at']
