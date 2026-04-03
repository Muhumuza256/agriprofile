from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from shared.permissions import IsSupervisorOrAbove, IsAnalystOrAbove
from apps.farmers.models import FarmerProfile
from .models import LoanCeilingCalculation
from .serializers import LoanCeilingSerializer, LoanCeilingSummarySerializer
from .engine import LoanCeilingEngine


class FarmerLoanCeilingListView(generics.ListAPIView):
    serializer_class = LoanCeilingSummarySerializer
    permission_classes = [IsAnalystOrAbove]

    def get_queryset(self):
        return LoanCeilingCalculation.objects.filter(
            farmer_id=self.kwargs['farmer_pk']
        ).order_by('-calculated_at')


class FarmerLoanCeilingLatestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, farmer_pk):
        calc = LoanCeilingCalculation.objects.filter(
            farmer_id=farmer_pk
        ).order_by('-calculated_at').first()
        if not calc:
            return Response(
                {'detail': 'No loan ceiling calculated yet.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(LoanCeilingSerializer(calc).data)


class CalculateLoanCeilingView(APIView):
    permission_classes = [IsSupervisorOrAbove]

    def post(self, request, farmer_pk):
        try:
            farmer = FarmerProfile.objects.prefetch_related('crops', 'plots').get(pk=farmer_pk)
        except FarmerProfile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        policy_id = request.data.get('policy_id')
        policy = None
        if policy_id:
            from apps.parameters.models import LoanPolicyParameter
            try:
                policy = LoanPolicyParameter.objects.get(id=policy_id, is_active=True)
            except LoanPolicyParameter.DoesNotExist:
                pass

        engine = LoanCeilingEngine()
        calc = engine.calculate_and_save(farmer, policy)
        return Response(LoanCeilingSerializer(calc).data, status=status.HTTP_201_CREATED)


class GroupLoanCeilingView(APIView):
    """Aggregated collective loan ceiling for a group."""
    permission_classes = [IsAuthenticated]

    def get(self, request, group_pk):
        from apps.groups.models import FarmerGroup
        try:
            group = FarmerGroup.objects.get(pk=group_pk)
        except FarmerGroup.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        calcs = LoanCeilingCalculation.objects.filter(
            farmer__group=group
        ).order_by('farmer', '-calculated_at').distinct('farmer')

        total_ceiling = sum(c.loan_ceiling_ugx for c in calcs)
        return Response({
            'group': str(group_pk),
            'group_name': group.name,
            'member_count': calcs.count(),
            'collective_loan_ceiling_ugx': float(total_ceiling),
            'collective_loan_ceiling_formatted': f"UGX {int(total_ceiling):,}",
        })
