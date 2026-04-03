from rest_framework import serializers
from .models import FarmerProfile, FarmerAsset, FarmerCrop


class FarmerCropSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerCrop
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'farmer']


class FarmerAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerAsset
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'farmer']


class FarmerProfileListSerializer(serializers.ModelSerializer):
    group_name          = serializers.CharField(source='group.name', read_only=True)
    profile_completeness = serializers.ReadOnlyField()
    dependant_ratio      = serializers.ReadOnlyField()

    class Meta:
        model = FarmerProfile
        fields = [
            'id', 'full_name', 'national_id', 'gender', 'district',
            'group', 'group_name', 'submission_status', 'is_active',
            'profile_completeness', 'dependant_ratio', 'created_at',
        ]


class FarmerProfileDetailSerializer(serializers.ModelSerializer):
    crops               = FarmerCropSerializer(many=True, read_only=True)
    assets              = FarmerAssetSerializer(read_only=True)
    profile_completeness = serializers.ReadOnlyField()
    dependant_ratio      = serializers.ReadOnlyField()
    gps_home             = serializers.JSONField(required=False, allow_null=True)
    agent_gps_at_entry   = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = FarmerProfile
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'submission_status', 'field_agent',
        ]

    def _parse_point(self, value):
        if value is None:
            return None
        from django.contrib.gis.geos import Point
        if isinstance(value, dict):
            if 'coordinates' in value:
                lon, lat = value['coordinates']
            elif 'lon' in value and 'lat' in value:
                lon, lat = value['lon'], value['lat']
            else:
                raise serializers.ValidationError('Invalid GPS format.')
            return Point(lon, lat, srid=4326)
        return value

    def create(self, validated_data):
        gps_home = validated_data.pop('gps_home', None)
        agent_gps = validated_data.pop('agent_gps_at_entry', None)
        farmer = FarmerProfile(**validated_data)
        farmer.gps_home = self._parse_point(gps_home)
        farmer.agent_gps_at_entry = self._parse_point(agent_gps)
        farmer.save()
        return farmer

    def update(self, instance, validated_data):
        gps_home = validated_data.pop('gps_home', None)
        agent_gps = validated_data.pop('agent_gps_at_entry', None)
        if gps_home is not None:
            instance.gps_home = self._parse_point(gps_home)
        if agent_gps is not None:
            instance.agent_gps_at_entry = self._parse_point(agent_gps)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
