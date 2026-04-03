from rest_framework import serializers
from .models import LoanCeilingCalculation


class LoanCeilingSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.full_name', read_only=True)
    loan_ceiling_ugx_formatted = serializers.SerializerMethodField()

    class Meta:
        model = LoanCeilingCalculation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'calculated_at']

    def get_loan_ceiling_ugx_formatted(self, obj):
        return f"UGX {int(obj.loan_ceiling_ugx):,}"


class LoanCeilingSummarySerializer(serializers.ModelSerializer):
    loan_ceiling_ugx_formatted = serializers.SerializerMethodField()

    class Meta:
        model = LoanCeilingCalculation
        fields = [
            'id', 'loan_ceiling_ugx', 'loan_ceiling_ugx_formatted',
            'agricultural_surplus_ugx', 'disbursement_month',
            'repayment_start_month', 'recommended_loan_term_months',
            'applicable_interest_rate', 'calculated_at',
        ]

    def get_loan_ceiling_ugx_formatted(self, obj):
        return f"UGX {int(obj.loan_ceiling_ugx):,}"
