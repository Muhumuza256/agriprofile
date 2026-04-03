"""
AgriProfile Credit Score (ACS) Calculation Engine
Weights: IVS=10%, LAS=20%, CPS=25%, GSS=20%, FBS=15%, HSS=10%
"""
from decimal import Decimal
from django.db.models import Sum

from .models import FarmerScore, GroupScore


class ACSEngine:
    """Calculates the individual AgriProfile Credit Score for a farmer."""

    WEIGHTS = {
        'ivs': Decimal('0.10'),
        'las': Decimal('0.20'),
        'cps': Decimal('0.25'),
        'gss': Decimal('0.20'),
        'fbs': Decimal('0.15'),
        'hss': Decimal('0.10'),
    }

    CREDIT_BANDS = [
        (Decimal('80'), 'platinum'),
        (Decimal('65'), 'gold'),
        (Decimal('50'), 'silver'),
        (Decimal('35'), 'bronze'),
        (Decimal('0'),  'unscored'),
    ]

    # Default CII values — overridden by CropIncomeIndex table
    CII_DEFAULTS = {
        'vanilla':       Decimal('2.0'),
        'coffee':        Decimal('1.8'),
        'cocoa':         Decimal('1.7'),
        'tea':           Decimal('1.6'),
        'passion fruit': Decimal('1.5'),
        'tomato':        Decimal('1.4'),
        'sunflower':     Decimal('1.3'),
        'maize':         Decimal('1.1'),
        'beans':         Decimal('1.0'),
        'sorghum':       Decimal('0.8'),
        'cassava':       Decimal('0.7'),
        'sweet potato':  Decimal('0.6'),
    }

    def __init__(self, farmer):
        self.farmer = farmer

    def calculate(self):
        """Run full ACS calculation. Returns an unsaved FarmerScore instance."""
        ivs = self._score_identity()
        las = self._score_land_assets()
        cps_raw = self._score_crop_production()
        cii = self._calculate_cii()
        cps = min(Decimal('100'), cps_raw * cii)
        gss = self._score_group_social()
        fbs = self._score_financial_behaviour()
        hss = self._score_household_stability()

        acs = (
            ivs * self.WEIGHTS['ivs'] +
            las * self.WEIGHTS['las'] +
            cps * self.WEIGHTS['cps'] +
            gss * self.WEIGHTS['gss'] +
            fbs * self.WEIGHTS['fbs'] +
            hss * self.WEIGHTS['hss']
        )

        saf = self._seasonal_adjustment_factor()
        acs_with_saf = min(Decimal('100'), max(Decimal('0'), acs + saf))
        band = self._determine_band(acs_with_saf)
        flags = self._generate_risk_flags(ivs, las, cps, gss, fbs, hss)

        return FarmerScore(
            farmer=self.farmer,
            ivs_score=ivs,
            las_score=las,
            cps_score=cps_raw,
            cps_adjusted=cps,
            gss_score=gss,
            fbs_score=fbs,
            hss_score=hss,
            cii_multiplier=cii,
            acs_score=acs.quantize(Decimal('0.01')),
            saf_modifier=saf,
            acs_with_saf=acs_with_saf.quantize(Decimal('0.01')),
            credit_band=band,
            risk_flags=flags,
            calculated_by='auto',
        )

    def calculate_and_save(self):
        score = self.calculate()
        score.save()
        return score

    # ── Dimension scorers ────────────────────────────────────────────────────

    def _score_identity(self):
        """IVS — Identity & Verification Score (out of 100)"""
        f = self.farmer
        score = Decimal('0')
        if f.national_id:         score += 30
        if f.portrait_photo:      score += 20
        if f.gps_home:            score += 20
        if f.primary_phone:       score += 15
        if f.next_of_kin_name:    score += 10
        if f.bank_account:        score += 5
        return score

    def _score_land_assets(self):
        """LAS — Land & Asset Score (out of 100)"""
        assets = getattr(self.farmer, 'assets', None)
        total_acres = self.farmer.plots.aggregate(
            Sum('area_acres'))['area_acres__sum'] or Decimal('0')
        score = Decimal('0')

        # Land size
        if total_acres > 5:       score += 80
        elif total_acres >= 2:    score += 60
        elif total_acres >= 0.5:  score += 30
        else:                     score += 10

        # Land tenure bonus
        tenure = self.farmer.plots.values_list('land_tenure', flat=True).first()
        if tenure in ('freehold', 'leasehold'):   score += 20
        elif tenure == 'mailo':                    score += 15
        elif tenure == 'customary':                score += 5

        # Assets
        if assets:
            if assets.owns_motorised_equipment:    score = min(score + 40, 100)
            elif assets.owns_animal_traction:      score = min(score + 20, 100)
            if assets.has_storage_structure:       score = min(score + 10, 100)
            if assets.has_irrigation:              score = min(score + 15, 100)
            cattle_pts = min(Decimal(str(assets.cattle_count)) * 3, 30)
            score = min(score + cattle_pts, 100)

        return min(score, Decimal('100'))

    def _score_crop_production(self):
        """CPS (raw) — Crop & Production Score before CII adjustment (out of 100)"""
        crops = self.farmer.crops.all()
        if not crops.exists():
            return Decimal('0')

        score = Decimal('0')
        crop_count = crops.count()

        # Crop diversity bonus
        if crop_count >= 3:   score += 20
        elif crop_count == 2: score += 10

        # Input and seed use
        crops_with_inputs = crops.filter(uses_inputs=True).count()
        crops_certified   = crops.filter(seed_source='certified').count()
        score += Decimal(str(min(crops_with_inputs * 10, 20)))
        score += Decimal(str(min(crops_certified * 10, 20)))

        # Market linkage
        commercial = crops.filter(sell_to__in=['off_taker', 'cooperative']).count()
        score += Decimal(str(min(commercial * 15, 30)))

        # Storage reduces post-harvest loss risk
        if crops.filter(has_storage=True).exists():
            score += 10

        return min(score, Decimal('100'))

    def _score_group_social(self):
        """GSS — Group & Social Capital Score (out of 100)"""
        group = self.farmer.group
        score = Decimal('0')

        if group:
            score += 30  # Group membership
            if group.is_registered:
                score += 20
            if group.has_bank_account:
                score += 15
            # Group loan history — repaid is positive
            repaid = group.loan_history.filter(status='repaid').count()
            defaulted = group.loan_history.filter(status='defaulted').count()
            score += Decimal(str(min(repaid * 10, 25)))
            score -= Decimal(str(defaulted * 20))

        # Individual financial account
        if self.farmer.bank_account or self.farmer.mobile_money_provider:
            score += 10

        return max(Decimal('0'), min(score, Decimal('100')))

    def _score_financial_behaviour(self):
        """FBS — Financial Behaviour Score (out of 100)"""
        f = self.farmer
        score = Decimal('0')

        if f.saves_regularly:              score += 30
        if f.monthly_savings_ugx > 0:     score += 20
        if f.has_prior_loan:
            if f.prior_loan_status == 'repaid':
                score += 40
            elif f.prior_loan_status == 'ongoing':
                score += 10
            elif f.prior_loan_status == 'defaulted':
                score -= 30
        else:
            score += 10  # No credit history — neutral

        if f.mobile_money_provider:        score += 10
        if f.bank_account:                 score += 10

        return max(Decimal('0'), min(score, Decimal('100')))

    def _score_household_stability(self):
        """HSS — Household Stability Score (out of 100)"""
        f = self.farmer
        score = Decimal('60')  # Neutral baseline

        # Working-age adults add stability
        if f.working_age_adults >= 3:   score += 20
        elif f.working_age_adults == 2: score += 10

        # High dependant ratio reduces stability
        dr = f.dependant_ratio
        if dr > 0.7:    score -= 20
        elif dr > 0.5:  score -= 10

        # Off-farm income diversification
        if f.off_farm_income_ugx > 0:   score += 20

        # Farm condition observation
        if f.farm_condition == 'excellent': score += 10
        elif f.farm_condition == 'good':    score += 5
        elif f.farm_condition == 'poor':    score -= 10

        return max(Decimal('0'), min(score, Decimal('100')))

    def _calculate_cii(self):
        """Crop Income Index — weighted average multiplier based on crop proportions."""
        crops = self.farmer.crops.all()
        total_acreage = sum(c.acreage for c in crops)
        if total_acreage == 0:
            return Decimal('1.0')

        weighted_cii = Decimal('0')
        for crop in crops:
            cii_val = self._get_cii_for_crop(crop.crop_name.lower())
            weight = crop.acreage / total_acreage
            weighted_cii += cii_val * weight

        return weighted_cii.quantize(Decimal('0.001'))

    def _get_cii_for_crop(self, crop_name):
        """Check admin parameters first, fall back to defaults."""
        try:
            from apps.parameters.models import CropIncomeIndex
            param = CropIncomeIndex.objects.get(
                crop_name__iexact=crop_name, is_active=True)
            return param.multiplier
        except Exception:
            return self.CII_DEFAULTS.get(crop_name, Decimal('1.0'))

    def _seasonal_adjustment_factor(self):
        """
        SAF — slight positive modifier during planting season,
        negative during lean season. Simple calendar-based.
        """
        from django.utils import timezone
        month = timezone.now().month
        # Lean season: Dec–Feb (post-harvest, pre-planting)
        if month in (12, 1, 2):
            return -3
        # Peak season: Mar–May, Sep–Nov
        if month in (3, 4, 5, 9, 10, 11):
            return 3
        return 0

    def _determine_band(self, score):
        for threshold, band in self.CREDIT_BANDS:
            if score >= threshold:
                return band
        return 'unscored'

    def _generate_risk_flags(self, ivs, las, cps, gss, fbs, hss):
        flags = []
        f = self.farmer

        if f.prior_loan_status == 'defaulted':
            flags.append({'level': 'red', 'message': 'Prior loan default recorded'})

        if gss < 20 and not f.bank_account and not f.mobile_money_provider:
            flags.append({'level': 'red',
                          'message': 'No group membership and no bank account'})

        if cps < 30:
            flags.append({'level': 'amber',
                          'message': 'Single subsistence crop, no inputs, no storage'})

        if f.dependant_ratio > 0.6 and f.off_farm_income_ugx == 0:
            flags.append({'level': 'amber',
                          'message': 'High dependant ratio with no off-farm income'})

        if ivs < 50:
            flags.append({'level': 'amber',
                          'message': 'Incomplete identity verification'})

        return flags


class GroupScoreEngine:
    """Calculates the Group AgriProfile Credit Score (GACS)."""

    def __init__(self, group):
        self.group = group

    def calculate(self):
        from apps.loans.models import LoanCeilingCalculation
        from django.db.models import Avg, Sum

        # Get latest score per member
        member_ids = self.group.members.filter(is_active=True).values_list('id', flat=True)
        if not member_ids:
            return None

        latest_scores = []
        for mid in member_ids:
            from apps.farmers.models import FarmerProfile
            farmer = FarmerProfile.objects.get(id=mid)
            score = farmer.scores.order_by('-calculated_at').first()
            if score:
                latest_scores.append(score)

        if not latest_scores:
            return None

        avg_acs = sum(s.acs_with_saf for s in latest_scores) / len(latest_scores)
        total_acres = self.group.members.aggregate(
            total=Sum('plots__area_acres'))['total'] or Decimal('0')

        # GACS = weighted average ACS with group bonuses
        gacs = avg_acs
        if self.group.is_registered:
            gacs = min(Decimal('100'), gacs + 3)
        if self.group.has_bank_account:
            gacs = min(Decimal('100'), gacs + 2)

        gacs = gacs.quantize(Decimal('0.01'))
        band = self._determine_band(gacs)

        group_score = GroupScore(
            group=self.group,
            member_count=len(latest_scores),
            avg_acs_score=avg_acs.quantize(Decimal('0.01')),
            gacs_score=gacs,
            credit_band=band,
            total_land_acres=total_acres,
        )
        return group_score

    def _determine_band(self, score):
        bands = [(80, 'platinum'), (65, 'gold'), (50, 'silver'), (35, 'bronze')]
        for threshold, band in bands:
            if score >= threshold:
                return band
        return 'unscored'
