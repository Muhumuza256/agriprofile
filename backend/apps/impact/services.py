from decimal import Decimal
from django.utils import timezone
from shared.utils import percentage_change
from .models import ImpactSnapshot


def create_baseline_snapshot(group):
    """
    Auto-creates the baseline ImpactSnapshot when a group is first approved.
    Reads current data from all active member profiles.
    """
    members = group.members.filter(is_active=True)
    member_count = members.count()

    # Land metrics
    from django.db.models import Sum
    total_land = members.aggregate(
        total=Sum('plots__area_acres'))['total'] or Decimal('0')
    cultivation = members.aggregate(
        total=Sum('crops__acreage'))['total'] or Decimal('0')

    # Crop diversity
    crops = list(
        members.values_list('crops__crop_name', flat=True)
        .distinct()
        .exclude(crops__crop_name=None)
    )

    # Certified seeds
    certified_farmers = members.filter(crops__seed_source='certified').distinct().count()
    fertiliser_farmers = members.filter(crops__uses_inputs=True).distinct().count()

    # Financial inclusion
    bank_members = members.exclude(bank_account='').count()
    mobile_members = members.exclude(mobile_money_provider='').count()

    # Asset data
    solar_members = members.filter(assets__has_solar=True).count()
    water_members = members.filter(assets__has_water_tank=True).count()
    storage_members = members.filter(assets__has_storage_structure=True).count()

    # GACS
    gacs_score = group.gacs

    snapshot = ImpactSnapshot.objects.create(
        group=group,
        snapshot_type='baseline',
        snapshot_date=timezone.now().date(),
        season_label=f"Baseline {timezone.now().year}",
        total_land_acres=total_land,
        land_under_cultivation_acres=cultivation,
        member_count=member_count,
        crops_grown=crops,
        using_certified_seeds_pct=(
            Decimal(str(certified_farmers / member_count * 100)) if member_count else Decimal('0')
        ),
        using_fertiliser_pct=(
            Decimal(str(fertiliser_farmers / member_count * 100)) if member_count else Decimal('0')
        ),
        members_with_bank_account=bank_members,
        members_with_mobile_money=mobile_members,
        members_with_solar=solar_members,
        members_with_water_tank=water_members,
        members_with_storage=storage_members,
        gacs_at_snapshot=Decimal(str(gacs_score)) if gacs_score else None,
    )
    return snapshot


class ImpactComparisonService:
    """Generates a 'then vs. now' comparison for a group."""

    def compare(self, group):
        snapshots = group.impact_snapshots.order_by('snapshot_date')
        if snapshots.count() < 2:
            return {
                'status': 'insufficient_data',
                'message': 'At least two snapshots required for comparison',
            }

        baseline = snapshots.first()
        latest   = snapshots.last()

        return {
            'group': group.name,
            'district': group.district,
            'period': {
                'from': str(baseline.snapshot_date),
                'to':   str(latest.snapshot_date),
                'seasons': snapshots.count() - 1,
            },
            'land': {
                'then': float(baseline.land_under_cultivation_acres),
                'now':  float(latest.land_under_cultivation_acres),
                'change_pct': percentage_change(
                    baseline.land_under_cultivation_acres,
                    latest.land_under_cultivation_acres),
            },
            'financial_inclusion': {
                'then': baseline.financial_inclusion_rate,
                'now':  latest.financial_inclusion_rate,
                'members_with_bank_then': baseline.members_with_bank_account,
                'members_with_bank_now':  latest.members_with_bank_account,
            },
            'credit': {
                'gacs_then': float(baseline.gacs_at_snapshot or 0),
                'gacs_now':  float(latest.gacs_at_snapshot or 0),
                'loans_disbursed_ugx': float(latest.total_loans_disbursed_ugx),
                'loan_cycles_completed': latest.loan_cycles_completed,
            },
            'assets': {
                'solar_then': baseline.members_with_solar,
                'solar_now':  latest.members_with_solar,
                'water_tank_then': baseline.members_with_water_tank,
                'water_tank_now':  latest.members_with_water_tank,
                'storage_then': baseline.members_with_storage,
                'storage_now':  latest.members_with_storage,
            },
            'agriculture': {
                'certified_seeds_then': float(baseline.using_certified_seeds_pct),
                'certified_seeds_now':  float(latest.using_certified_seeds_pct),
                'harvest_then': float(baseline.estimated_harvest_tonnes),
                'harvest_now':  float(latest.estimated_harvest_tonnes),
                'crops_grown': latest.crops_grown,
            },
            'programmes': {
                'training_sessions': latest.training_sessions_received,
                'ngo_programmes': latest.ngo_programmes_enrolled,
                'linked_to_off_taker': latest.linked_to_off_taker,
            },
        }
