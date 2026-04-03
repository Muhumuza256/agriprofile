from decimal import Decimal
from django.db import models
from shared.models import BaseModel


class LoanCeilingCalculation(BaseModel):
    """
    Stores the complete farm income calculation that produces the loan ceiling.
    Uses admin-configured parameters for prices, costs, and yields.
    """
    farmer             = models.ForeignKey(
                           'farmers.FarmerProfile', on_delete=models.CASCADE,
                           related_name='loan_calculations')
    parameters_version = models.CharField(max_length=50)
    calculated_at      = models.DateTimeField(auto_now_add=True)

    # Revenue
    gross_revenue_ugx    = models.DecimalField(max_digits=15, decimal_places=2)
    realised_revenue_ugx = models.DecimalField(max_digits=15, decimal_places=2)

    # Cost deductions
    pre_planting_costs_ugx    = models.DecimalField(max_digits=15, decimal_places=2)
    growing_costs_ugx         = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    post_harvest_costs_ugx    = models.DecimalField(max_digits=15, decimal_places=2)
    transport_costs_ugx       = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    household_expenditure_ugx = models.DecimalField(max_digits=15, decimal_places=2)

    # Net figures
    net_farm_income_ugx      = models.DecimalField(max_digits=15, decimal_places=2)
    agricultural_surplus_ugx = models.DecimalField(max_digits=15, decimal_places=2)

    # Loan recommendation
    repayment_threshold      = models.DecimalField(
                                 max_digits=4, decimal_places=2, default=Decimal('0.35'))
    applicable_interest_rate = models.DecimalField(max_digits=5, decimal_places=4)
    loan_ceiling_ugx         = models.DecimalField(max_digits=15, decimal_places=2)

    # Timing recommendations
    disbursement_month              = models.PositiveIntegerField()  # 1–12
    repayment_start_month           = models.PositiveIntegerField()  # 1–12
    recommended_loan_term_months    = models.PositiveIntegerField()
    repayment_free_months           = models.PositiveIntegerField(default=0)

    # Crop breakdown snapshot
    crop_calculations = models.JSONField(default=list)

    class Meta:
        db_table = 'loans_ceiling_calculation'
        ordering = ['-calculated_at']

    def __str__(self):
        return f"{self.farmer.full_name} — UGX {self.loan_ceiling_ugx:,.0f}"
