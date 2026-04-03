from django.db import models
from django.db.models import Sum
from django.contrib.gis.db import models as gis_models
from shared.models import BaseModel


class GroupType(models.TextChoices):
    VSLA          = 'vsla',          'Village Savings & Loan Association'
    ROSCA         = 'rosca',         'Rotating Savings & Credit Association'
    SACCO         = 'sacco',         'Savings & Credit Cooperative'
    COOPERATIVE   = 'cooperative',   'Registered Cooperative'
    FARMERS_GROUP = 'farmers_group', 'Farmers Group'
    OTHER         = 'other',         'Other'


class RegistrationBody(models.TextChoices):
    CDO    = 'cdo',    'Community Development Officer'
    PARISH = 'parish', 'Parish Level'
    RCS    = 'rcs',    'Registrar of Companies'
    MTIC   = 'mtic',   'Ministry of Trade, Industry & Cooperatives'
    BOU    = 'bou',    'Bank of Uganda'
    OTHER  = 'other',  'Other'


class FarmerGroup(BaseModel):
    """
    Primary entity. All farmer profiles, plots, and scores are anchored to a FarmerGroup.
    """
    # Identity
    name                  = models.CharField(max_length=255)
    group_type            = models.CharField(max_length=30, choices=GroupType.choices)
    registration_number   = models.CharField(max_length=100, blank=True)
    registration_body     = models.CharField(
                              max_length=20, choices=RegistrationBody.choices, blank=True)
    registration_date     = models.DateField(null=True, blank=True)
    registration_document = models.ImageField(
                              upload_to='groups/registration/', blank=True)
    is_registered         = models.BooleanField(default=False)

    # Location
    village       = models.CharField(max_length=100)
    parish        = models.CharField(max_length=100)
    sub_county    = models.CharField(max_length=100)
    district      = models.CharField(max_length=100)
    gps_meeting_point = gis_models.PointField(null=True, blank=True, srid=4326)

    # Leadership
    chairperson_name  = models.CharField(max_length=200)
    chairperson_phone = models.CharField(max_length=20)
    secretary_name    = models.CharField(max_length=200, blank=True)
    treasurer_name    = models.CharField(max_length=200, blank=True)

    # Financial
    has_bank_account    = models.BooleanField(default=False)
    bank_name           = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    has_mobile_money    = models.BooleanField(default=False)

    # Meta
    registered_by = models.ForeignKey(
                      'accounts.User', on_delete=models.SET_NULL,
                      null=True, related_name='registered_groups')
    is_approved   = models.BooleanField(default=False)
    approved_by   = models.ForeignKey(
                      'accounts.User', on_delete=models.SET_NULL,
                      null=True, blank=True, related_name='approved_groups')
    approved_at   = models.DateTimeField(null=True, blank=True)
    notes         = models.TextField(blank=True)

    class Meta:
        db_table = 'groups_farmer_group'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.district}"

    @property
    def member_count(self):
        return self.members.filter(is_active=True).count()

    @property
    def total_land_acres(self):
        return self.members.aggregate(
            total=Sum('plots__area_acres')
        )['total'] or 0

    @property
    def gacs(self):
        """Returns the latest Group AgriProfile Credit Score."""
        latest = self.scores.order_by('-calculated_at').first()
        return float(latest.gacs_score) if latest else None


class GroupLoanHistory(BaseModel):
    """Records prior loan history for the group as a unit."""
    group           = models.ForeignKey(
                        FarmerGroup, on_delete=models.CASCADE,
                        related_name='loan_history')
    institution     = models.CharField(max_length=200)
    loan_amount_ugx = models.DecimalField(max_digits=15, decimal_places=2)
    loan_date       = models.DateField()
    purpose         = models.CharField(max_length=200)
    status          = models.CharField(max_length=20, choices=[
                        ('repaid', 'Fully Repaid'),
                        ('ongoing', 'Ongoing'),
                        ('defaulted', 'Defaulted'),
                      ])
    notes           = models.TextField(blank=True)

    class Meta:
        db_table = 'groups_loan_history'
        ordering = ['-loan_date']

    def __str__(self):
        return f"{self.group.name} — {self.institution} ({self.status})"
