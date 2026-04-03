from django.contrib import admin
from .models import FarmerProfile, FarmerAsset, FarmerCrop


class FarmerCropInline(admin.TabularInline):
    model = FarmerCrop
    extra = 0
    fields = ['crop_name', 'acreage', 'season', 'sell_to', 'uses_inputs']


class FarmerAssetInline(admin.StackedInline):
    model = FarmerAsset
    extra = 0


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'national_id', 'gender', 'district',
        'group', 'submission_status', 'is_active', 'created_at',
    ]
    list_filter = ['gender', 'district', 'submission_status', 'is_active', 'primary_income_source']
    search_fields = ['full_name', 'national_id', 'primary_phone']
    readonly_fields = ['id', 'created_at', 'updated_at', 'dependant_ratio', 'profile_completeness']
    inlines = [FarmerCropInline, FarmerAssetInline]
