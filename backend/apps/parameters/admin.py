from django.contrib import admin
from .models import CropParameter, CropIncomeIndex, LoanPolicyParameter, ParameterAuditLog


@admin.register(CropParameter)
class CropParameterAdmin(admin.ModelAdmin):
    list_display = ['crop_name', 'farm_gate_price_ugx_per_kg', 'price_volatility', 'is_active', 'effective_from']
    list_filter = ['price_volatility', 'is_active']
    search_fields = ['crop_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(CropIncomeIndex)
class CropIncomeIndexAdmin(admin.ModelAdmin):
    list_display = ['crop_name', 'multiplier', 'tier', 'is_active']
    list_filter = ['tier', 'is_active']


@admin.register(LoanPolicyParameter)
class LoanPolicyAdmin(admin.ModelAdmin):
    list_display = ['institution_name', 'annual_interest_rate', 'minimum_acs_score', 'is_default', 'is_active']
    list_filter = ['is_active', 'is_default']


@admin.register(ParameterAuditLog)
class ParameterAuditLogAdmin(admin.ModelAdmin):
    list_display = ['parameter_model', 'field_changed', 'changed_by', 'created_at', 'recalculation_queued']
    list_filter = ['parameter_model', 'recalculation_queued']
    readonly_fields = ['id', 'created_at', 'updated_at']
