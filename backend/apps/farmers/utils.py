REQUIRED_FIELDS = [
    'full_name', 'national_id', 'date_of_birth', 'gender',
    'primary_phone', 'village', 'parish', 'sub_county', 'district',
    'next_of_kin_name', 'next_of_kin_phone',
    'household_size',
]

OPTIONAL_SCORED_FIELDS = [
    'national_id_photo', 'portrait_photo', 'gps_home',
    'mobile_money_provider', 'bank_account',
    'visit_date', 'farm_condition', 'homestead_type',
]


def calculate_completeness(farmer):
    """
    Returns a percentage (0–100) of how complete the farmer's profile is.
    Weights required fields at 70%, optional scored fields at 30%.
    """
    required_filled = sum(
        1 for f in REQUIRED_FIELDS
        if getattr(farmer, f, None) not in (None, '', 0)
    )
    optional_filled = sum(
        1 for f in OPTIONAL_SCORED_FIELDS
        if getattr(farmer, f, None) not in (None, '', False)
    )

    # Also check related records
    has_crops = farmer.crops.exists() if farmer.pk else False
    has_assets = hasattr(farmer, 'assets')
    has_plots = farmer.plots.exists() if farmer.pk else False

    required_score = (required_filled / len(REQUIRED_FIELDS)) * 70
    optional_score = (optional_filled / len(OPTIONAL_SCORED_FIELDS)) * 20
    relations_score = (
        (3 if has_crops else 0) +
        (4 if has_assets else 0) +
        (3 if has_plots else 0)
    )

    return round(min(required_score + optional_score + relations_score, 100), 1)
