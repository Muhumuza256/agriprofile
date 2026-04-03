from django.db import models
from shared.models import BaseModel


class FarmActivity(BaseModel):
    """
    Locally tracked farm activity. Synced to OpenAgri FarmCalendar service.
    """
    ACTIVITY_CHOICES = [
        ('land_preparation', 'Land Preparation'),
        ('planting',         'Planting'),
        ('top_dressing',     'Top Dressing'),
        ('pest_control',     'Pest & Disease Control'),
        ('weeding',          'Weeding'),
        ('harvesting',       'Harvesting'),
        ('post_harvest',     'Post-Harvest Processing'),
        ('storage',          'Storage'),
        ('marketing',        'Marketing'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
    ]

    farmer_crop       = models.ForeignKey(
                          'farmers.FarmerCrop', on_delete=models.CASCADE,
                          related_name='activities')
    activity_type     = models.CharField(max_length=30, choices=ACTIVITY_CHOICES)
    scheduled_date    = models.DateField()
    completed_date    = models.DateField(null=True, blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes             = models.TextField(blank=True)

    # OpenAgri FarmCalendar sync
    calendar_activity_id = models.CharField(max_length=100, blank=True)
    synced_at            = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'calendar_farm_activity'
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.farmer_crop.crop_name} — {self.activity_type} ({self.scheduled_date})"
