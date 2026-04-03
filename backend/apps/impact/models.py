from django.db import models
from shared.models import BaseModel


class ImpactSnapshot(BaseModel):
    """
    Point-in-time snapshot of a group's key impact indicators.
    Baseline captured at registration. Updated each season.
    """
    group = models.ForeignKey(
              'groups.FarmerGroup', on_delete=models.CASCADE,
              related_name='impact_snapshots')
    snapshot_type = models.CharField(max_length=20, choices=[
                      ('baseline', 'Baseline — Registration'),
                      ('season',   'Seasonal Update'),
                      ('annual',   'Annual Review'),
                    ])
    snapshot_date = models.DateField()
    season_label  = models.CharField(max_length=50, blank=True)

    # Agricultural indicators
    total_land_acres              = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    land_under_cultivation_acres  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    member_count                  = models.PositiveIntegerField(default=0)
    crops_grown                   = models.JSONField(default=list)
    using_certified_seeds_pct     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    using_fertiliser_pct          = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estimated_harvest_tonnes      = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Financial inclusion indicators
    members_with_bank_account   = models.PositiveIntegerField(default=0)
    members_with_mobile_money   = models.PositiveIntegerField(default=0)
    members_with_formal_credit  = models.PositiveIntegerField(default=0)
    total_loans_disbursed_ugx   = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loan_cycles_completed       = models.PositiveIntegerField(default=0)

    # Asset & infrastructure indicators
    members_with_solar          = models.PositiveIntegerField(default=0)
    members_with_water_tank     = models.PositiveIntegerField(default=0)
    members_with_clean_cooking  = models.PositiveIntegerField(default=0)
    members_with_storage        = models.PositiveIntegerField(default=0)

    # Programme participation
    training_sessions_received  = models.PositiveIntegerField(default=0)
    smart_practices_adopted_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    linked_to_off_taker         = models.BooleanField(default=False)
    bulk_input_purchases        = models.PositiveIntegerField(default=0)
    ngo_programmes_enrolled     = models.JSONField(default=list)

    # Credit score
    avg_acs_at_snapshot  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    gacs_at_snapshot     = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Narrative
    field_notes  = models.TextField(blank=True)
    captured_by  = models.ForeignKey(
                     'accounts.User', on_delete=models.SET_NULL, null=True,
                     related_name='captured_snapshots')

    class Meta:
        db_table = 'impact_snapshot'
        ordering = ['snapshot_date']

    def __str__(self):
        return f"{self.group.name} — {self.snapshot_type} ({self.snapshot_date})"

    @property
    def financial_inclusion_rate(self):
        if self.member_count == 0:
            return 0
        return round(
            (self.members_with_bank_account + self.members_with_mobile_money) /
            (self.member_count * 2) * 100, 1
        )
