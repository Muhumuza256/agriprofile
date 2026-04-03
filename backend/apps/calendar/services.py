import json
import requests
from datetime import date, timedelta
from django.conf import settings

from .models import FarmActivity


class FarmCalendarService:
    """
    Proxy service that synchronises AgriProfile plot and crop data
    with the OpenAgri FarmCalendar service.
    """

    BASE_URL = settings.OPENAGRI_CALENDAR_URL

    def _get_headers(self):
        try:
            resp = requests.post(
                f"{self.BASE_URL}/api/token/",
                data={
                    'username': settings.OPENAGRI_CALENDAR_USERNAME,
                    'password': settings.OPENAGRI_CALENDAR_PASSWORD,
                },
                timeout=5,
            )
            if resp.status_code == 200:
                token = resp.json().get('access', '')
                return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        except requests.RequestException:
            pass
        return {'Content-Type': 'application/json'}

    def _post(self, endpoint, payload):
        try:
            resp = requests.post(
                f"{self.BASE_URL}{endpoint}",
                json=payload,
                headers=self._get_headers(),
                timeout=10,
            )
            return resp.json() if resp.status_code in (200, 201) else None
        except requests.RequestException:
            return None

    def register_parcel(self, plot):
        """Register a mapped farm plot as a parcel in FarmCalendar."""
        payload = {
            'name': f"{plot.farmer.full_name} — {plot.plot_name}",
            'area': float(plot.area_acres or 0),
            'geometry': json.loads(plot.boundary.geojson) if plot.boundary else None,
            'external_id': str(plot.id),
        }
        result = self._post('/api/v1/parcels/', payload)
        if result and 'id' in result:
            plot.calendar_parcel_id = str(result['id'])
            plot.save(update_fields=['calendar_parcel_id'])
        return result

    def log_activity(self, farmer_crop, activity_type, scheduled_date):
        """Log a farming activity to FarmCalendar."""
        from apps.plots.models import FarmPlot
        plot = FarmPlot.objects.filter(farmer=farmer_crop.farmer).first()
        parcel_id = plot.calendar_parcel_id if plot else None

        payload = {
            'parcel': parcel_id,
            'activity_type': activity_type,
            'scheduled_date': scheduled_date.isoformat() if hasattr(scheduled_date, 'isoformat') else str(scheduled_date),
            'crop': farmer_crop.crop_name,
        }
        return self._post('/api/v1/activities/', payload)

    def generate_season_calendar(self, farmer_crop):
        """
        Auto-generate a full season calendar for a crop based on planting month,
        crop duration, and seasonal logic.
        """
        today = date.today()
        planting = date(today.year, farmer_crop.planting_month, 1)

        activities = [
            ('land_preparation', planting - timedelta(weeks=4)),
            ('planting',         planting),
            ('top_dressing',     planting + timedelta(weeks=6)),
            ('pest_control',     planting + timedelta(weeks=8)),
            ('weeding',          planting + timedelta(weeks=4)),
            ('harvesting',       date(today.year, farmer_crop.harvest_month, 1)),
            ('post_harvest',     date(today.year, farmer_crop.harvest_month, 15)),
        ]

        created = []
        for activity_type, scheduled_date in activities:
            activity, _ = FarmActivity.objects.get_or_create(
                farmer_crop=farmer_crop,
                activity_type=activity_type,
                defaults={'scheduled_date': scheduled_date},
            )
            created.append(activity)

            # Sync to OpenAgri
            result = self.log_activity(farmer_crop, activity_type, scheduled_date)
            if result and 'id' in result:
                from django.utils import timezone
                activity.calendar_activity_id = str(result['id'])
                activity.synced_at = timezone.now()
                activity.save(update_fields=['calendar_activity_id', 'synced_at'])

        return created
