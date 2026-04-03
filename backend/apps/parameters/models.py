from decimal import Decimal
from django.db import models
from shared.models import BaseModel


class CropParameter(BaseModel):
    """Admin-configurable crop economics. Updated each season."""
    crop_name                       = models.CharField(max_length=100, unique=True)
    farm_gate_price_ugx_per_kg      = models.DecimalField(max_digits=10, decimal_places=2)
    market_price_ugx_per_kg         = models.DecimalField(max_digits=10, decimal_places=2)
    benchmark_yield_kg_per_acre_low  = models.DecimalField(max_digits=8, decimal_places=2)
    benchmark_yield_kg_per_acre_high = models.DecimalField(max_digits=8, decimal_places=2)
    seed_cost_ugx_per_acre          = models.DecimalField(max_digits=10, decimal_places=2)
    fertiliser_cost_ugx_per_acre    = models.DecimalField(max_digits=10, decimal_places=2)
    land_prep_cost_ugx_per_acre     = models.DecimalField(max_digits=10, decimal_places=2)
    labour_cost_ugx_per_acre        = models.DecimalField(max_digits=10, decimal_places=2)
    transport_cost_ugx_per_acre     = models.DecimalField(max_digits=10, decimal_places=2)
    post_harvest_loss_pct_default   = models.DecimalField(max_digits=5, decimal_places=2)
    price_volatility                = models.CharField(max_length=20, choices=[
                                        ('stable', 'Stable'),
                                        ('moderate', 'Moderate'),
                                        ('volatile', 'Volatile'),
                                      ])
    is_active           = models.BooleanField(default=True)
    last_updated_by     = models.ForeignKey(
                            'accounts.User', on_delete=models.SET_NULL, null=True,
                            related_name='updated_parameters')
    effective_from      = models.DateField()
    notes               = models.TextField(blank=True)

    class Meta:
        db_table = 'parameters_crop'
        ordering = ['crop_name']

    def __str__(self):
        return f"{self.crop_name} (UGX {self.farm_gate_price_ugx_per_kg}/kg)"

    @property
    def benchmark_yield_mid(self):
        return (self.benchmark_yield_kg_per_acre_low +
                self.benchmark_yield_kg_per_acre_high) / 2


class CropIncomeIndex(BaseModel):
    """Crop Income Index multipliers — adjusts CPS score for crop value."""
    crop_name  = models.CharField(max_length=100, unique=True)
    multiplier = models.DecimalField(max_digits=4, decimal_places=3)
    tier       = models.CharField(max_length=20, choices=[
                   ('tier_1', 'Tier 1 — Export Cash'),
                   ('tier_2', 'Tier 2 — Commercial'),
                   ('tier_3', 'Tier 3 — Staple Cash'),
                   ('tier_4', 'Tier 4 — Subsistence'),
                 ])
    is_active  = models.BooleanField(default=True)

    class Meta:
        db_table = 'parameters_crop_income_index'
        ordering = ['-multiplier']
        verbose_name = 'Crop Income Index'
        verbose_name_plural = 'Crop Income Indices'

    def __str__(self):
        return f"{self.crop_name} × {self.multiplier} ({self.tier})"


class LoanPolicyParameter(BaseModel):
    """Bank/institution-specific lending policy parameters."""
    institution_name           = models.CharField(max_length=200)
    annual_interest_rate       = models.DecimalField(max_digits=5, decimal_places=4)
    repayment_income_threshold = models.DecimalField(
                                   max_digits=4, decimal_places=2,
                                   default=Decimal('0.35'))
    minimum_loan_ugx           = models.DecimalField(max_digits=15, decimal_places=2)
    maximum_loan_ugx           = models.DecimalField(max_digits=15, decimal_places=2)
    minimum_acs_score          = models.DecimalField(max_digits=5, decimal_places=2)
    is_default                 = models.BooleanField(default=False)
    is_active                  = models.BooleanField(default=True)

    class Meta:
        db_table = 'parameters_loan_policy'
        ordering = ['institution_name']

    def __str__(self):
        return f"{self.institution_name} — {float(self.annual_interest_rate * 100):.1f}%"


class ParameterAuditLog(BaseModel):
    """
    Every parameter change is logged for institutional audit trail.
    A parameter change triggers a Celery score recalculation.
    """
    parameter_model      = models.CharField(max_length=100)
    parameter_id         = models.UUIDField()
    field_changed        = models.CharField(max_length=100)
    old_value            = models.TextField()
    new_value            = models.TextField()
    changed_by           = models.ForeignKey(
                             'accounts.User', on_delete=models.SET_NULL, null=True,
                             related_name='parameter_changes')
    recalculation_queued = models.BooleanField(default=False)
    farmers_affected     = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'parameters_audit_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.parameter_model}.{self.field_changed} @ {self.created_at}"
