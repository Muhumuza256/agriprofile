from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'role', 'district', 'is_active']
    list_filter = ['role', 'is_active', 'district']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('AgriProfile', {'fields': ('role', 'phone', 'district', 'organisation', 'last_sync')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('AgriProfile', {'fields': ('role', 'phone', 'district', 'organisation')}),
    )
