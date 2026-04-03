"""
Loan Ceiling Calculator Engine
Implements the farm income statement model.

Formula:
  Gross Revenue = Σ(Acreage × Yield × Reliability × Farm Gate Price)
  Realised Revenue = Gross Revenue × (1 - Post Harvest Loss %)
  Net Farm Income = Realised Revenue - All Production Costs
  Agricultural Surplus = Net Farm Income - Household Expenditure
  Loan Ceiling = Agricultural Surplus × 0.35 / (1 + interest_rate)
"""
from decimal import Decimal

from .models import LoanCeilingCalculation


class LoanCeilingEngine:

    HOUSEHOLD_EXPENDITURE_PER_PERSON_UGX = Decimal('150000')  # monthly per person

    def calculate(self, farmer, policy=None):
        params = self._load_parameters()
        interest_rate = Decimal(str(policy.annual_interest_rate)) if policy else \
                        params.get('default_interest_rate', Decimal('0.20'))
        repayment_threshold = Decimal(str(policy.repayment_income_threshold)) if policy else \
                              Decimal('0.35')

        crop_calcs = []
        total_gross = Decimal('0')
        total_costs = Decimal('0')

        for crop in farmer.crops.all():
            calc = self._calculate_crop_income(crop, params)
            crop_calcs.append(calc)
            total_gross += Decimal(str(calc['realised_revenue']))
            total_costs += Decimal(str(calc['total_costs']))

        household_exp = (
            Decimal(str(farmer.household_size)) *
            self.HOUSEHOLD_EXPENDITURE_PER_PERSON_UGX * 12  # annual
        )

        net_income = total_gross - total_costs
        surplus = max(net_income - household_exp, Decimal('0'))
        ceiling = max((surplus * repayment_threshold) / (1 + interest_rate), Decimal('0'))

        # Hard zero for prior defaulters
        if farmer.prior_loan_status == 'defaulted':
            ceiling = Decimal('0')

        windows = self._calculate_timing_windows(farmer)
        version = self._get_parameter_version()

        return LoanCeilingCalculation(
            farmer=farmer,
            parameters_version=version,
            gross_revenue_ugx=total_gross,
            realised_revenue_ugx=total_gross,
            pre_planting_costs_ugx=sum(
                Decimal(str(c['pre_planting_cost'])) for c in crop_calcs
            ),
            growing_costs_ugx=Decimal('0'),
            post_harvest_costs_ugx=sum(
                Decimal(str(c['post_harvest_cost'])) for c in crop_calcs
            ),
            transport_costs_ugx=Decimal('0'),
            household_expenditure_ugx=household_exp,
            net_farm_income_ugx=net_income,
            agricultural_surplus_ugx=surplus,
            loan_ceiling_ugx=ceiling.quantize(Decimal('1')),
            applicable_interest_rate=interest_rate,
            repayment_threshold=repayment_threshold,
            crop_calculations=crop_calcs,
            **windows,
        )

    def calculate_and_save(self, farmer, policy=None):
        calc = self.calculate(farmer, policy)
        calc.save()
        return calc

    def _calculate_crop_income(self, crop, params):
        crop_params = params['crops'].get(crop.crop_name.lower(), {})
        farm_gate_price = Decimal(str(
            crop_params.get('farm_gate_price_ugx_per_kg', 0)
        ))
        benchmark_yield = Decimal(str(
            crop_params.get('benchmark_yield_mid', 0)
        ))

        yield_per_acre = crop.expected_yield_kg_per_acre or benchmark_yield
        reliability = self._reliability_factor(crop)

        gross = crop.acreage * yield_per_acre * reliability * farm_gate_price
        loss_factor = 1 - (crop.post_harvest_loss_pct / 100)
        realised = gross * loss_factor

        seed_cost = Decimal(str(crop_params.get('seed_cost_ugx_per_acre', 0)))
        land_prep  = Decimal(str(crop_params.get('land_prep_cost_ugx_per_acre', 0)))
        labour     = Decimal(str(crop_params.get('labour_cost_ugx_per_acre', 0)))
        fertiliser = Decimal(str(crop_params.get('fertiliser_cost_ugx_per_acre', 0))) \
                     if crop.uses_inputs else Decimal('0')
        transport  = Decimal(str(crop_params.get('transport_cost_ugx_per_acre', 0)))

        pre_planting = crop.acreage * (seed_cost + land_prep + labour + fertiliser)
        post_harvest = crop.acreage * transport

        return {
            'crop_name':         crop.crop_name,
            'acreage':           float(crop.acreage),
            'yield_per_acre':    float(yield_per_acre),
            'reliability_factor': float(reliability),
            'farm_gate_price':   float(farm_gate_price),
            'gross_revenue':     float(gross),
            'realised_revenue':  float(realised),
            'pre_planting_cost': float(pre_planting),
            'post_harvest_cost': float(post_harvest),
            'total_costs':       float(pre_planting + post_harvest),
        }

    @staticmethod
    def _reliability_factor(crop):
        """Conservative yield factor based on farmer experience and inputs."""
        if (crop.seasons_farmed >= 3 and crop.uses_inputs
                and crop.seed_source == 'certified'):
            return Decimal('0.90')
        elif crop.seasons_farmed >= 2:
            return Decimal('0.75')
        return Decimal('0.55')

    @staticmethod
    def _calculate_timing_windows(farmer):
        """
        Determine optimal disbursement and repayment windows
        from the farmer's crop calendar.
        """
        crops = farmer.crops.all()
        if not crops.exists():
            return {
                'disbursement_month': 3,
                'repayment_start_month': 8,
                'recommended_loan_term_months': 6,
                'repayment_free_months': 4,
            }

        # Use the earliest planting month and latest harvest month
        planting_months = [c.planting_month for c in crops]
        harvest_months  = [c.harvest_month  for c in crops]

        disbursement = min(planting_months)
        repayment_start = max(harvest_months)

        # Calculate term
        if repayment_start >= disbursement:
            term = repayment_start - disbursement + 2
        else:  # harvest crosses year boundary
            term = (12 - disbursement) + repayment_start + 2

        free_months = max(repayment_start - disbursement, 0)

        return {
            'disbursement_month': disbursement,
            'repayment_start_month': repayment_start,
            'recommended_loan_term_months': min(term, 12),
            'repayment_free_months': free_months,
        }

    @staticmethod
    def _load_parameters():
        """Load crop parameters from database, keyed by crop name."""
        from apps.parameters.models import CropParameter
        params = {'crops': {}}
        for p in CropParameter.objects.filter(is_active=True):
            params['crops'][p.crop_name.lower()] = {
                'farm_gate_price_ugx_per_kg':  float(p.farm_gate_price_ugx_per_kg),
                'benchmark_yield_mid':          float(p.benchmark_yield_mid),
                'seed_cost_ugx_per_acre':       float(p.seed_cost_ugx_per_acre),
                'land_prep_cost_ugx_per_acre':  float(p.land_prep_cost_ugx_per_acre),
                'labour_cost_ugx_per_acre':     float(p.labour_cost_ugx_per_acre),
                'fertiliser_cost_ugx_per_acre': float(p.fertiliser_cost_ugx_per_acre),
                'transport_cost_ugx_per_acre':  float(p.transport_cost_ugx_per_acre),
            }
        return params

    @staticmethod
    def _get_parameter_version():
        from django.utils import timezone
        return f"v{timezone.now().strftime('%Y%m%d')}"
