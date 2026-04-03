from django.contrib import admin
from .models import FarmActivity


@admin.register(FarmActivity)
class FarmActivityAdmin(admin.ModelAdmin):
    list_display = ['farmer_crop', 'activity_type', 'scheduled_date', 'status', 'synced_at']
    list_filter = ['activity_type', 'status']
    search_fields = ['farmer_crop__crop_name', 'farmer_crop__farmer__full_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'synced_at']
