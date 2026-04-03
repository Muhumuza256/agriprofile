from rest_framework import serializers
from .models import CropParameter, CropIncomeIndex, LoanPolicyParameter, ParameterAuditLog


class CropParameterSerializer(serializers.ModelSerializer):
    benchmark_yield_mid = serializers.ReadOnlyField()

    class Meta:
        model = CropParameter
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_updated_by']


class CropIncomeIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropIncomeIndex
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class LoanPolicyParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanPolicyParameter
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ParameterAuditLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)

    class Meta:
        model = ParameterAuditLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
