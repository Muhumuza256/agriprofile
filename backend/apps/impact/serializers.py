from rest_framework import serializers
from .models import ImpactSnapshot


class ImpactSnapshotSerializer(serializers.ModelSerializer):
    financial_inclusion_rate = serializers.ReadOnlyField()
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = ImpactSnapshot
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'captured_by']
