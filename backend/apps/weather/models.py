from django.db import models
from shared.models import BaseModel


class PlotWeatherSnapshot(BaseModel):
    """Cached weather data for a farm plot. Refreshed every 6 hours by Celery."""
    plot             = models.OneToOneField(
                         'plots.FarmPlot', on_delete=models.CASCADE,
                         related_name='weather')
    forecast_data    = models.JSONField(default=dict)
    fetched_at       = models.DateTimeField()
    condition_summary = models.CharField(max_length=100, blank=True)
    rainfall_7day_mm  = models.DecimalField(
                          max_digits=8, decimal_places=2, null=True, blank=True)
    temperature_max_c = models.DecimalField(
                          max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_min_c = models.DecimalField(
                          max_digits=5, decimal_places=2, null=True, blank=True)
    humidity_pct      = models.DecimalField(
                          max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'weather_plot_snapshot'

    def __str__(self):
        return f"Weather for {self.plot} @ {self.fetched_at}"
