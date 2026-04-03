from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Sum

from shared.permissions import IsAnalystOrAbove, IsPartnerOrAbove
from apps.accounts.models import UserRole


class OverviewView(APIView):
    """Top-level KPIs for the main dashboard."""
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        from apps.farmers.models import FarmerProfile
        from apps.groups.models import FarmerGroup
        from apps.scoring.models import FarmerScore

        total_farmers = FarmerProfile.objects.filter(is_active=True).count()
        total_groups  = FarmerGroup.objects.filter(is_approved=True).count()
        districts     = FarmerProfile.objects.values_list(
                          'district', flat=True).distinct().count()

        avg_acs = FarmerScore.objects.order_by(
            'farmer', '-calculated_at'
        ).distinct('farmer').aggregate(avg=Avg('acs_with_saf'))['avg'] or 0

        pending_submissions = FarmerProfile.objects.filter(
            submission_status='pending').count()

        return Response({
            'total_farmers':        total_farmers,
            'total_groups':         total_groups,
            'districts_covered':    districts,
            'avg_acs_score':        round(float(avg_acs), 2),
            'pending_submissions':  pending_submissions,
        })


class ScoreDistributionView(APIView):
    """ACS band breakdown across all scored farmers."""
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        from apps.scoring.models import FarmerScore

        distribution = (
            FarmerScore.objects
            .order_by('farmer', '-calculated_at')
            .distinct('farmer')
            .values('credit_band')
            .annotate(count=Count('id'))
        )

        return Response(list(distribution))


class CropIntelligenceView(APIView):
    """Crops by farmer count, acreage, district, and season."""
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        from apps.farmers.models import FarmerCrop

        crops = (
            FarmerCrop.objects
            .values('crop_name', 'season', 'crop_category')
            .annotate(
                farmer_count=Count('farmer', distinct=True),
                total_acreage=Sum('acreage'),
            )
            .order_by('-total_acreage')
        )

        return Response(list(crops))


class SeasonalWindowsView(APIView):
    """Optimal disbursement and repayment windows by crop."""
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        from apps.farmers.models import FarmerCrop

        windows = (
            FarmerCrop.objects
            .values('crop_name', 'planting_month', 'harvest_month')
            .annotate(farmer_count=Count('farmer', distinct=True))
            .order_by('planting_month')
        )

        return Response(list(windows))


class DistrictProfileView(APIView):
    """District-level agricultural summary."""
    permission_classes = [IsPartnerOrAbove]

    def get(self, request, district):
        from apps.farmers.models import FarmerProfile, FarmerCrop
        from apps.scoring.models import FarmerScore

        farmers = FarmerProfile.objects.filter(
            district__iexact=district, is_active=True)

        if not farmers.exists():
            return Response({'detail': f'No data for district: {district}'}, status=404)

        avg_acs = FarmerScore.objects.filter(
            farmer__district__iexact=district
        ).order_by('farmer', '-calculated_at').distinct('farmer').aggregate(
            avg=Avg('acs_with_saf'))['avg'] or 0

        crops = (
            FarmerCrop.objects.filter(farmer__district__iexact=district)
            .values('crop_name')
            .annotate(count=Count('id'), total_acres=Sum('acreage'))
            .order_by('-total_acres')
        )

        return Response({
            'district': district,
            'farmer_count': farmers.count(),
            'avg_acs_score': round(float(avg_acs), 2),
            'unbanked_count': farmers.filter(bank_account='', mobile_money_provider='').count(),
            'top_crops': list(crops[:10]),
        })


class AgentPerformanceView(APIView):
    """Field agent submission statistics."""
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        from apps.farmers.models import FarmerProfile

        perf = (
            FarmerProfile.objects
            .values('field_agent__first_name', 'field_agent__last_name',
                    'field_agent_id')
            .annotate(
                total_submitted=Count('id'),
                approved=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(submission_status='approved')),
            )
            .order_by('-total_submitted')
        )

        return Response(list(perf))


class ImpactSummaryView(APIView):
    """Aggregated impact across all groups."""
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        from apps.impact.models import ImpactSnapshot

        latest_baselines = ImpactSnapshot.objects.filter(
            snapshot_type='baseline'
        )
        latest_updates = ImpactSnapshot.objects.filter(
            snapshot_type__in=['season', 'annual']
        )

        return Response({
            'groups_with_baseline': latest_baselines.values('group').distinct().count(),
            'groups_with_updates': latest_updates.values('group').distinct().count(),
            'total_members_tracked': latest_baselines.aggregate(s=Sum('member_count'))['s'] or 0,
            'total_loans_disbursed_ugx': float(
                latest_updates.aggregate(s=Sum('total_loans_disbursed_ugx'))['s'] or 0
            ),
        })


class GroupMapView(APIView):
    """GeoJSON of all approved group meeting points."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.groups.models import FarmerGroup
        import json

        groups = FarmerGroup.objects.filter(
            is_approved=True,
            gps_meeting_point__isnull=False,
        )

        features = []
        for g in groups:
            features.append({
                'type': 'Feature',
                'geometry': json.loads(g.gps_meeting_point.geojson),
                'properties': {
                    'id': str(g.id),
                    'name': g.name,
                    'district': g.district,
                    'member_count': g.member_count,
                    'gacs': g.gacs,
                },
            })

        return Response({'type': 'FeatureCollection', 'features': features})
