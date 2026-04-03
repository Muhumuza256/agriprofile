from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import FarmerGroup, GroupLoanHistory


class GroupLoanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLoanHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class FarmerGroupListSerializer(serializers.ModelSerializer):
    """Lightweight serialiser for list views and partner access."""
    member_count     = serializers.ReadOnlyField()
    total_land_acres = serializers.ReadOnlyField()
    gacs             = serializers.ReadOnlyField()

    class Meta:
        model = FarmerGroup
        fields = [
            'id', 'name', 'group_type', 'district', 'sub_county', 'village',
            'is_registered', 'is_approved', 'member_count',
            'total_land_acres', 'gacs', 'created_at',
        ]


class FarmerGroupDetailSerializer(serializers.ModelSerializer):
    """Full serialiser for detail views."""
    member_count     = serializers.ReadOnlyField()
    total_land_acres = serializers.ReadOnlyField()
    gacs             = serializers.ReadOnlyField()
    loan_history     = GroupLoanHistorySerializer(many=True, read_only=True)
    gps_meeting_point = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = FarmerGroup
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'is_approved', 'approved_by', 'approved_at',
            'registered_by',
        ]

    def _parse_point(self, value):
        """Accept either GeoJSON dict or raw {lat, lon} dict."""
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
        gps = validated_data.pop('gps_meeting_point', None)
        group = FarmerGroup(**validated_data)
        group.gps_meeting_point = self._parse_point(gps)
        group.save()
        return group

    def update(self, instance, validated_data):
        gps = validated_data.pop('gps_meeting_point', None)
        if gps is not None:
            instance.gps_meeting_point = self._parse_point(gps)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
