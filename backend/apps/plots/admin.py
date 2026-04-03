from django.contrib.gis import admin
from .models import FarmPlot


@admin.register(FarmPlot)
class FarmPlotAdmin(admin.GISModelAdmin):
    list_display = ['plot_name', 'farmer', 'area_acres', 'land_tenure', 'is_verified', 'created_at']
    list_filter = ['land_tenure', 'is_verified', 'soil_type', 'terrain']
    search_fields = ['plot_name', 'farmer__full_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'area_acres', 'centre_point']
