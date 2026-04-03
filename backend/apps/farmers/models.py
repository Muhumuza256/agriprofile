from django.db import models
from django.contrib.gis.db import models as gis_models
from shared.models import BaseModel


class FarmerProfile(BaseModel):
    """
    Individual farmer profile. Always belongs to a FarmerGroup.
    Data collected across 8 modules by a field agent.
    """
    # Module A — Identity
    group             = models.ForeignKey(
                          'groups.FarmerGroup', on_delete=models.CASCADE,
                          related_name='members')
    full_name         = models.CharField(max_length=255)
    national_id       = models.CharField(max_length=50, unique=True)
    national_id_photo = models.ImageField(upload_to='farmers/ids/', blank=True)
    portrait_photo    = models.ImageField(upload_to='farmers/portraits/', blank=True)
    date_of_birth     = models.DateField(null=True, blank=True)
    gender            = models.CharField(max_length=10, choices=[
                          ('male', 'Male'), ('female', 'Female'), ('other', 'Other')
                        ])
    primary_phone           = models.CharField(max_length=20)
    mobile_money_provider   = models.CharField(max_length=50, blank=True)
    bank_name               = models.CharField(max_length=100, blank=True)
    bank_account            = models.CharField(max_length=50, blank=True)
    village                 = models.CharField(max_length=100)
    parish                  = models.CharField(max_length=100)
    sub_county              = models.CharField(max_length=100)
    district                = models.CharField(max_length=100)
    gps_home                = gis_models.PointField(null=True, blank=True, srid=4326)
    next_of_kin_name        = models.CharField(max_length=200)
    next_of_kin_phone       = models.CharField(max_length=20)

    # Module B — Household
    household_size        = models.PositiveIntegerField(default=1)
    dependants            = models.PositiveIntegerField(default=0)
    working_age_adults    = models.PositiveIntegerField(default=1)
    farm_labour_available = models.PositiveIntegerField(default=1)
    primary_income_source = models.CharField(max_length=20, choices=[
                              ('farming', 'Farming'),
                              ('mixed', 'Mixed'),
                              ('other', 'Other'),
                            ], default='farming')
    off_farm_income_ugx   = models.DecimalField(
                              max_digits=12, decimal_places=2, default=0)

    # Module G — Financial History
    has_prior_loan    = models.BooleanField(default=False)
    prior_loan_source = models.CharField(max_length=50, blank=True)
    prior_loan_status = models.CharField(max_length=20, blank=True, choices=[
                          ('repaid', 'Repaid'),
                          ('ongoing', 'Ongoing'),
                          ('defaulted', 'Defaulted'),
                        ])
    saves_regularly     = models.BooleanField(default=False)
    saving_method       = models.CharField(max_length=50, blank=True)
    monthly_savings_ugx = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Module H — Field Agent Observations
    farm_condition   = models.CharField(max_length=20, choices=[
                         ('excellent', 'Excellent'), ('good', 'Good'),
                         ('fair', 'Fair'), ('poor', 'Poor'),
                       ], blank=True)
    homestead_type   = models.CharField(max_length=20, choices=[
                         ('permanent', 'Permanent'),
                         ('semi_permanent', 'Semi-permanent'),
                         ('temporary', 'Temporary'),
                       ], blank=True)
    agent_notes         = models.TextField(blank=True)
    visit_date          = models.DateField(null=True, blank=True)
    agent_gps_at_entry  = gis_models.PointField(null=True, blank=True, srid=4326)
    field_agent         = models.ForeignKey(
                            'accounts.User', on_delete=models.SET_NULL, null=True,
                            related_name='profiled_farmers')
    submission_status   = models.CharField(max_length=20, default='pending', choices=[
                            ('pending', 'Pending Review'),
                            ('approved', 'Approved'),
                            ('rejected', 'Rejected'),
                          ])
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'farmers_farmer_profile'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.group.name}"

    @property
    def dependant_ratio(self):
        if self.household_size == 0:
            return 0
        return round(self.dependants / self.household_size, 2)

    @property
    def profile_completeness(self):
        from .utils import calculate_completeness
        return calculate_completeness(self)


class FarmerAsset(BaseModel):
    """Module E — Farm assets and equipment."""
    farmer                   = models.OneToOneField(
                                 FarmerProfile, on_delete=models.CASCADE,
                                 related_name='assets')
    owns_hand_tools          = models.BooleanField(default=False)
    owns_animal_traction     = models.BooleanField(default=False)
    owns_motorised_equipment = models.BooleanField(default=False)
    equipment_description    = models.TextField(blank=True)
    has_storage_structure    = models.BooleanField(default=False)
    storage_capacity_bags    = models.PositiveIntegerField(default=0)
    cattle_count             = models.PositiveIntegerField(default=0)
    goats_count              = models.PositiveIntegerField(default=0)
    pigs_count               = models.PositiveIntegerField(default=0)
    poultry_count            = models.PositiveIntegerField(default=0)
    has_irrigation           = models.BooleanField(default=False)
    has_solar                = models.BooleanField(default=False)
    has_water_tank           = models.BooleanField(default=False)
    transport_type           = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'farmers_farmer_asset'


class FarmerCrop(BaseModel):
    """
    Module D — One record per crop per farmer.
    Multiple crops per farmer are supported.
    """
    farmer        = models.ForeignKey(
                      FarmerProfile, on_delete=models.CASCADE, related_name='crops')
    crop_name     = models.CharField(max_length=100)
    crop_category = models.CharField(max_length=20, choices=[
                      ('subsistence', 'Subsistence'),
                      ('cash', 'Cash Crop'),
                      ('both', 'Both'),
                    ])
    season        = models.CharField(max_length=20, choices=[
                      ('season_a', 'Season A'),
                      ('season_b', 'Season B'),
                      ('both', 'Both Seasons'),
                      ('perennial', 'Perennial'),
                    ])
    planting_month = models.PositiveIntegerField()   # 1–12
    harvest_month  = models.PositiveIntegerField()   # 1–12
    acreage        = models.DecimalField(max_digits=6, decimal_places=2)
    seed_source    = models.CharField(max_length=20, choices=[
                       ('certified', 'Certified'),
                       ('saved', 'Saved'),
                       ('market', 'Market'),
                     ])
    uses_inputs    = models.BooleanField(default=False)
    expected_yield_kg_per_acre      = models.DecimalField(
                                        max_digits=8, decimal_places=2)
    actual_yield_last_season_kg     = models.DecimalField(
                                        max_digits=10, decimal_places=2,
                                        null=True, blank=True)
    sell_to = models.CharField(max_length=30, choices=[
                ('home_use', 'Home Use'),
                ('local_market', 'Local Market'),
                ('trader', 'Trader/Middleman'),
                ('off_taker', 'Formal Off-taker'),
                ('cooperative', 'Cooperative'),
              ])
    seasons_farmed          = models.PositiveIntegerField(default=1)
    has_storage             = models.BooleanField(default=False)
    post_harvest_loss_pct   = models.DecimalField(
                                max_digits=5, decimal_places=2, default=20)
    crop_loss_last_season_pct = models.DecimalField(
                                  max_digits=5, decimal_places=2, default=0)
    crop_loss_cause         = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = 'farmers_farmer_crop'
        ordering = ['crop_name']

    def __str__(self):
        return f"{self.farmer.full_name} — {self.crop_name} ({self.acreage} ac)"
