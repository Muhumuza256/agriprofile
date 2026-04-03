from django.db import models
from django.contrib.gis.db import models as gis_models
from shared.models import BaseModel


class FarmPlot(BaseModel):
    """
    A GPS-mapped farm plot belonging to a farmer.
    One farmer can have multiple plots.
    Boundary stored as a PostGIS Polygon.
    Area calculated from boundary polygon.
    """
    farmer          = models.ForeignKey(
                        'farmers.FarmerProfile', on_delete=models.CASCADE,
                        related_name='plots')
    plot_name       = models.CharField(max_length=100, default='Main Plot')
    boundary        = gis_models.PolygonField(null=True, blank=True, srid=4326)
    centre_point    = gis_models.PointField(null=True, blank=True, srid=4326)
    area_acres      = models.DecimalField(
                        max_digits=8, decimal_places=3, null=True, blank=True)
    gps_accuracy_m  = models.DecimalField(
                        max_digits=6, decimal_places=2, null=True, blank=True)
    is_verified     = models.BooleanField(default=False)
    measurement_date = models.DateField(null=True, blank=True)
    mapped_by       = models.ForeignKey(
                        'accounts.User', on_delete=models.SET_NULL, null=True,
                        related_name='mapped_plots')
    primary_crop    = models.ForeignKey(
                        'farmers.FarmerCrop', on_delete=models.SET_NULL,
                        null=True, blank=True, related_name='plots')
    land_tenure     = models.CharField(max_length=20, choices=[
                        ('customary', 'Customary'),
                        ('leasehold', 'Leasehold'),
                        ('freehold', 'Freehold'),
                        ('mailo', 'Mailo'),
                      ])
    has_title_document = models.BooleanField(default=False)
    soil_type       = models.CharField(max_length=20, blank=True, choices=[
                        ('clay', 'Clay'), ('loam', 'Loam'),
                        ('sandy', 'Sandy'), ('mixed', 'Mixed'),
                      ])
    terrain         = models.CharField(max_length=20, blank=True, choices=[
                        ('flat', 'Flat'),
                        ('gentle_slope', 'Gentle Slope'),
                        ('steep', 'Steep'),
                      ])
    water_source    = models.CharField(max_length=50, blank=True)
    plot_photos     = models.JSONField(default=list)

    # OpenAgri FarmCalendar parcel ID for sync
    calendar_parcel_id = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'plots_farm_plot'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.farmer.full_name} — {self.plot_name} ({self.area_acres} ac)"

    def save(self, *args, **kwargs):
        if self.boundary:
            self.area_acres = self._calculate_area_acres()
            self.centre_point = self.boundary.centroid
        super().save(*args, **kwargs)

    def _calculate_area_acres(self):
        """Convert PostGIS polygon area to acres using geodesic transform."""
        from django.contrib.gis.geos import GEOSGeometry
        import json
        # Transform to Web Mercator (metres) for area calculation
        poly_3857 = self.boundary.transform(3857, clone=True)
        area_m2 = poly_3857.area
        return round(area_m2 / 4046.86, 3)
