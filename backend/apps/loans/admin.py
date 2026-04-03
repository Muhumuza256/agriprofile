from django.contrib import admin
from .models import LoanCeilingCalculation


@admin.register(LoanCeilingCalculation)
class LoanCeilingAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'loan_ceiling_ugx', 'agricultural_surplus_ugx',
                    'disbursement_month', 'repayment_start_month', 'calculated_at']
    list_filter = ['disbursement_month', 'repayment_start_month']
    search_fields = ['farmer__full_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'calculated_at']
