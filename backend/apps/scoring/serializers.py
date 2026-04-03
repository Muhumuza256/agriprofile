from rest_framework import serializers
from .models import FarmerScore, GroupScore


class FarmerScoreSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.full_name', read_only=True)

    class Meta:
        model = FarmerScore
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'calculated_at']


class FarmerScoreSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerScore
        fields = [
            'id', 'acs_with_saf', 'credit_band', 'calculated_at',
            'ivs_score', 'las_score', 'cps_score', 'gss_score',
            'fbs_score', 'hss_score', 'risk_flags',
        ]


class GroupScoreSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = GroupScore
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'calculated_at']
