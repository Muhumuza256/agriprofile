import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('agriprofile')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'fetch-weather-every-6-hours': {
        'task': 'apps.weather.tasks.fetch_weather_for_all_active_plots',
        'schedule': 21600,  # 6 hours in seconds
    },
}
