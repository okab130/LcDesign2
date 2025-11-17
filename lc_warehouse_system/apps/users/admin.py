from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['user_id', 'user_name', 'user_type', 'base_code', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['user_id', 'user_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('user_id', 'password')}),
        ('個人情報', {'fields': ('user_name', 'user_type', 'base_code')}),
        ('権限', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('日時情報', {'fields': ('created_at', 'updated_at', 'last_login')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_id', 'user_name', 'user_type', 'base_code', 'password1', 'password2', 'is_active'),
        }),
    )
    
    ordering = ['user_id']
