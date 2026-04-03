from decimal import Decimal
from rest_framework import serializers
from django.contrib.gis.geos import Polygon
from .models import FarmPlot


class PlotListSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.full_name', read_only=True)

    class Meta:
        model = FarmPlot
        fields = [
            'id', 'farmer', 'farmer_name', 'plot_name', 'area_acres',
            'land_tenure', 'is_verified', 'soil_type', 'terrain', 'created_at',
        ]


class PlotCreateSerializer(serializers.ModelSerializer):
    """
    Accepts a list of {lat, lon} coordinate dicts and converts to a PostGIS polygon.
    """
    coordinates = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        min_length=3,
        help_text='List of {lat, lon} dicts defining the plot boundary.',
    )

    class Meta:
        model = FarmPlot
        fields = [
            'farmer', 'plot_name', 'coordinates', 'gps_accuracy_m',
            'land_tenure', 'has_title_document', 'soil_type',
            'terrain', 'water_source', 'primary_crop', 'measurement_date',
        ]

    def validate_coordinates(self, coords):
        for c in coords:
            if 'lat' not in c or 'lon' not in c:
                raise serializers.ValidationError(
                    'Each coordinate must have "lat" and "lon" keys.'
                )
        return coords

    def create(self, validated_data):
        coords = validated_data.pop('coordinates')
        polygon = self._coords_to_polygon(coords)
        validated_data['boundary'] = polygon
        return FarmPlot.objects.create(**validated_data)

    @staticmethod
    def _coords_to_polygon(coords):
        points = [(c['lon'], c['lat']) for c in coords]
        if points[0] != points[-1]:
            points.append(points[0])  # auto-close
        return Polygon(points, srid=4326)


class PlotDetailSerializer(serializers.ModelSerializer):
    farmer_name  = serializers.CharField(source='farmer.full_name', read_only=True)
    boundary_geojson = serializers.SerializerMethodField()

    class Meta:
        model = FarmPlot
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'area_acres', 'centre_point']

    def get_boundary_geojson(self, obj):
        if obj.boundary:
            import json
            return json.loads(obj.boundary.geojson)
        return None
