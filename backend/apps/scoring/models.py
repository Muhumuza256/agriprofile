from django.db import models
from shared.models import BaseModel


class FarmerScore(BaseModel):
    """
    Stores ACS calculation result per farmer per scoring run.
    Recalculated whenever profile data changes.
    """
    farmer        = models.ForeignKey(
                      'farmers.FarmerProfile', on_delete=models.CASCADE,
                      related_name='scores')
    calculated_at = models.DateTimeField(auto_now_add=True)
    calculated_by = models.CharField(max_length=20, choices=[
                      ('auto', 'Automatic'), ('manual', 'Manual')
                    ])

    # Dimension scores (each out of 100)
    ivs_score = models.DecimalField(max_digits=5, decimal_places=2)  # Identity
    las_score = models.DecimalField(max_digits=5, decimal_places=2)  # Land & Assets
    cps_score = models.DecimalField(max_digits=5, decimal_places=2)  # Crop & Production
    gss_score = models.DecimalField(max_digits=5, decimal_places=2)  # Group & Social
    fbs_score = models.DecimalField(max_digits=5, decimal_places=2)  # Financial Behaviour
    hss_score = models.DecimalField(max_digits=5, decimal_places=2)  # Household Stability

    # Weighted composite
    acs_score   = models.DecimalField(max_digits=5, decimal_places=2)
    credit_band = models.CharField(max_length=20, choices=[
                    ('platinum', 'Platinum'),
                    ('gold', 'Gold'),
                    ('silver', 'Silver'),
                    ('bronze', 'Bronze'),
                    ('unscored', 'Unscored'),
                  ])

    # CII and SAF adjustments
    cii_multiplier = models.DecimalField(max_digits=4, decimal_places=3, default=1.0)
    cps_adjusted   = models.DecimalField(max_digits=5, decimal_places=2)
    saf_modifier   = models.IntegerField(default=0)
    acs_with_saf   = models.DecimalField(max_digits=5, decimal_places=2)

    # Risk flags
    risk_flags  = models.JSONField(default=list)
    score_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'scoring_farmer_score'
        ordering = ['-calculated_at']

    def __str__(self):
        return f"{self.farmer.full_name} — ACS {self.acs_with_saf} ({self.credit_band})"


class GroupScore(BaseModel):
    """Aggregate GACS score for a FarmerGroup."""
    group           = models.ForeignKey(
                        'groups.FarmerGroup', on_delete=models.CASCADE,
                        related_name='scores')
    calculated_at   = models.DateTimeField(auto_now_add=True)
    member_count    = models.PositiveIntegerField()
    avg_acs_score   = models.DecimalField(max_digits=5, decimal_places=2)
    gacs_score      = models.DecimalField(max_digits=5, decimal_places=2)
    credit_band     = models.CharField(max_length=20)
    total_land_acres = models.DecimalField(max_digits=10, decimal_places=2)
    collective_loan_ceiling_ugx = models.DecimalField(
                                    max_digits=15, decimal_places=2, default=0)
    risk_flags = models.JSONField(default=list)

    class Meta:
        db_table = 'scoring_group_score'
        ordering = ['-calculated_at']

    def __str__(self):
        return f"{self.group.name} — GACS {self.gacs_score} ({self.credit_band})"
