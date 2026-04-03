from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import PlotWeatherSnapshot
from .tasks import fetch_weather_for_plot


class PlotWeatherView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, plot_pk):
        try:
            snapshot = PlotWeatherSnapshot.objects.get(plot_id=plot_pk)
            return Response({
                'plot_id': str(plot_pk),
                'condition': snapshot.condition_summary,
                'rainfall_7day_mm': float(snapshot.rainfall_7day_mm or 0),
                'temperature_max_c': float(snapshot.temperature_max_c or 0),
                'temperature_min_c': float(snapshot.temperature_min_c or 0),
                'humidity_pct': float(snapshot.humidity_pct or 0),
                'fetched_at': snapshot.fetched_at,
                'forecast': snapshot.forecast_data,
            })
        except PlotWeatherSnapshot.DoesNotExist:
            # Trigger a fresh fetch
            fetch_weather_for_plot.delay(str(plot_pk))
            return Response(
                {'detail': 'Weather data not yet available. Fetch queued.'},
                status=status.HTTP_202_ACCEPTED,
            )


class GroupWeatherView(APIView):
    """Aggregated weather summary across all plots in a group."""
    permission_classes = [IsAuthenticated]

    def get(self, request, group_pk):
        snapshots = PlotWeatherSnapshot.objects.filter(
            plot__farmer__group_id=group_pk
        )
        if not snapshots.exists():
            return Response({'detail': 'No weather data available.'}, status=status.HTTP_404_NOT_FOUND)

        rainfalls = [s.rainfall_7day_mm for s in snapshots if s.rainfall_7day_mm]
        avg_rainfall = sum(rainfalls) / len(rainfalls) if rainfalls else 0

        return Response({
            'group_id': str(group_pk),
            'plot_count': snapshots.count(),
            'avg_rainfall_7day_mm': float(avg_rainfall),
            'plots': [
                {
                    'plot_id': str(s.plot_id),
                    'condition': s.condition_summary,
                    'rainfall_7day_mm': float(s.rainfall_7day_mm or 0),
                    'fetched_at': s.fetched_at,
                }
                for s in snapshots
            ],
        })
