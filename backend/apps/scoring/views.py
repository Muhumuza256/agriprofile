from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from shared.permissions import IsSupervisorOrAbove, IsAnalystOrAbove
from .models import FarmerScore, GroupScore
from .serializers import FarmerScoreSerializer, FarmerScoreSummarySerializer, GroupScoreSerializer


class FarmerScoreListView(generics.ListAPIView):
    serializer_class = FarmerScoreSummarySerializer
    permission_classes = [IsAnalystOrAbove]

    def get_queryset(self):
        return FarmerScore.objects.filter(
            farmer_id=self.kwargs['farmer_pk']
        ).order_by('-calculated_at')


class FarmerLatestScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, farmer_pk):
        score = FarmerScore.objects.filter(
            farmer_id=farmer_pk
        ).order_by('-calculated_at').first()
        if not score:
            return Response({'detail': 'No score calculated yet.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(FarmerScoreSerializer(score).data)


class TriggerScoreCalculationView(APIView):
    permission_classes = [IsSupervisorOrAbove]

    def post(self, request, farmer_pk):
        from .tasks import calculate_farmer_score
        calculate_farmer_score.delay(str(farmer_pk))
        return Response({'detail': 'Score calculation queued.'})


class GroupScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_pk):
        score = GroupScore.objects.filter(
            group_id=group_pk
        ).order_by('-calculated_at').first()
        if not score:
            return Response({'detail': 'No group score calculated yet.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(GroupScoreSerializer(score).data)
