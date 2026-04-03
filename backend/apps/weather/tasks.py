import requests
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def _get_weather_token():
    """Obtain auth token from OpenAgri WeatherService."""
    response = requests.post(
        f"{settings.OPENAGRI_WEATHER_URL}/api/token/",
        data={
            'username': settings.OPENAGRI_WEATHER_USERNAME,
            'password': settings.OPENAGRI_WEATHER_PASSWORD,
        },
        timeout=5,
    )
    if response.status_code == 200:
        return response.json().get('access', '')
    return ''


def _extract_condition_summary(data):
    try:
        return data['list'][0]['weather'][0]['description'].title()
    except (KeyError, IndexError):
        return 'Unknown'


def _extract_rainfall_total(data):
    total = 0.0
    try:
        for item in data.get('list', []):
            total += item.get('rain', {}).get('3h', 0)
    except Exception:
        pass
    return round(total, 2)


def _extract_temp(data, key):
    try:
        return data['list'][0]['main'][key]
    except (KeyError, IndexError):
        return None


@shared_task
def fetch_weather_for_plot(plot_id):
    """
    Fetches 5-day forecast from OpenAgri WeatherService for a specific
    farm plot's centre point. Results cached in Redis for 6 hours.
    """
    from apps.plots.models import FarmPlot
    from .models import PlotWeatherSnapshot

    try:
        plot = FarmPlot.objects.get(id=plot_id)
    except FarmPlot.DoesNotExist:
        return {'error': f'Plot {plot_id} not found'}

    if not plot.centre_point:
        return {'skipped': 'No centre point'}

    lat = plot.centre_point.y
    lon = plot.centre_point.x

    cache_key = f"weather:plot:{plot_id}"
    cached = cache.get(cache_key)
    if cached:
        return {'cached': True, 'plot_id': plot_id}

    try:
        token = _get_weather_token()
        response = requests.get(
            f"{settings.OPENAGRI_WEATHER_URL}/api/data/forecast5/",
            params={'lat': lat, 'lon': lon},
            headers={'Authorization': f'Bearer {token}'} if token else {},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            cache.set(cache_key, data, timeout=21600)  # 6 hours

            PlotWeatherSnapshot.objects.update_or_create(
                plot=plot,
                defaults={
                    'forecast_data': data,
                    'fetched_at': timezone.now(),
                    'condition_summary': _extract_condition_summary(data),
                    'rainfall_7day_mm': _extract_rainfall_total(data),
                    'temperature_max_c': _extract_temp(data, 'temp_max'),
                    'temperature_min_c': _extract_temp(data, 'temp_min'),
                    'humidity_pct': _extract_temp(data, 'humidity'),
                },
            )
            return {'plot_id': plot_id, 'status': 'updated'}
        return {'error': f'Weather service returned {response.status_code}'}
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}


@shared_task
def fetch_weather_for_all_active_plots():
    """Scheduled task — runs every 6 hours via Celery Beat."""
    from apps.plots.models import FarmPlot
    ids = FarmPlot.objects.filter(
        farmer__group__is_approved=True,
        centre_point__isnull=False,
    ).values_list('id', flat=True)

    for plot_id in ids:
        fetch_weather_for_plot.delay(str(plot_id))

    return {'queued': len(ids)}
