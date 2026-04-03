from django.contrib import admin
from .models import FarmerScore, GroupScore


@admin.register(FarmerScore)
class FarmerScoreAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'acs_with_saf', 'credit_band', 'calculated_at', 'calculated_by']
    list_filter = ['credit_band', 'calculated_by']
    search_fields = ['farmer__full_name', 'farmer__national_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'calculated_at']


@admin.register(GroupScore)
class GroupScoreAdmin(admin.ModelAdmin):
    list_display = ['group', 'gacs_score', 'credit_band', 'member_count', 'calculated_at']
    list_filter = ['credit_band']
    readonly_fields = ['id', 'created_at', 'updated_at', 'calculated_at']
