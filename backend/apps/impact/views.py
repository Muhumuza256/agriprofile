from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from shared.permissions import IsFieldAgentOrAbove, IsAnalystOrAbove
from apps.groups.models import FarmerGroup
from .models import ImpactSnapshot
from .serializers import ImpactSnapshotSerializer
from .services import ImpactComparisonService, create_baseline_snapshot


class GroupSnapshotListCreateView(generics.ListCreateAPIView):
    serializer_class = ImpactSnapshotSerializer
    permission_classes = [IsFieldAgentOrAbove]

    def get_queryset(self):
        return ImpactSnapshot.objects.filter(group_id=self.kwargs['group_pk'])

    def perform_create(self, serializer):
        group = FarmerGroup.objects.get(pk=self.kwargs['group_pk'])
        serializer.save(group=group, captured_by=self.request.user)


class GroupComparisonView(APIView):
    """Returns the then vs. now impact comparison for a group."""
    permission_classes = [IsAuthenticated]

    def get(self, request, group_pk):
        try:
            group = FarmerGroup.objects.get(pk=group_pk)
        except FarmerGroup.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        service = ImpactComparisonService()
        comparison = service.compare(group)
        return Response(comparison)


class RefreshBaselineView(APIView):
    """Manually refresh/create the baseline snapshot for a group."""
    permission_classes = [IsAnalystOrAbove]

    def post(self, request, group_pk):
        try:
            group = FarmerGroup.objects.get(pk=group_pk)
        except FarmerGroup.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        snapshot = create_baseline_snapshot(group)
        return Response(ImpactSnapshotSerializer(snapshot).data, status=status.HTTP_201_CREATED)
