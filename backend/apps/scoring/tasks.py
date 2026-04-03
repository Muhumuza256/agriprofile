from celery import shared_task


@shared_task
def calculate_farmer_score(farmer_id):
    """Calculate and save ACS for a specific farmer."""
    from apps.farmers.models import FarmerProfile
    from .engine import ACSEngine
    try:
        farmer = FarmerProfile.objects.get(id=farmer_id)
        engine = ACSEngine(farmer)
        score = engine.calculate_and_save()
        # Recalculate the group score too
        calculate_group_score.delay(str(farmer.group_id))
        return {'farmer_id': farmer_id, 'acs_score': float(score.acs_with_saf)}
    except FarmerProfile.DoesNotExist:
        return {'error': f'Farmer {farmer_id} not found'}


@shared_task
def calculate_group_score(group_id):
    """Aggregate GACS for a group from member scores."""
    from apps.groups.models import FarmerGroup
    from .engine import GroupScoreEngine
    try:
        group = FarmerGroup.objects.get(id=group_id)
        engine = GroupScoreEngine(group)
        score = engine.calculate()
        if score:
            score.save()
            return {'group_id': group_id, 'gacs_score': float(score.gacs_score)}
        return {'group_id': group_id, 'gacs_score': None}
    except FarmerGroup.DoesNotExist:
        return {'error': f'Group {group_id} not found'}


@shared_task
def recalculate_all_scores():
    """Recalculate all active farmer scores. Triggered when parameters change."""
    from apps.farmers.models import FarmerProfile
    ids = FarmerProfile.objects.filter(
        is_active=True, submission_status='approved'
    ).values_list('id', flat=True)
    for fid in ids:
        calculate_farmer_score.delay(str(fid))
    return {'queued': len(ids)}
