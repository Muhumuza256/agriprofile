from django.contrib import admin
from .models import PlotWeatherSnapshot


@admin.register(PlotWeatherSnapshot)
class PlotWeatherSnapshotAdmin(admin.ModelAdmin):
    list_display = ['plot', 'condition_summary', 'rainfall_7day_mm', 'fetched_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'fetched_at']
