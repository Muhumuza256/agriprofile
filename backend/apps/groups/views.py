from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from shared.permissions import IsFieldAgentOrAbove, IsSupervisorOrAbove, IsPartnerOrAbove
from apps.accounts.models import UserRole
from .models import FarmerGroup, GroupLoanHistory
from .serializers import (
    FarmerGroupListSerializer,
    FarmerGroupDetailSerializer,
    GroupLoanHistorySerializer,
)


class FarmerGroupListCreateView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['district', 'sub_county', 'group_type', 'is_approved', 'is_registered']
    search_fields = ['name', 'district', 'chairperson_name']
    ordering_fields = ['created_at', 'name', 'district']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsFieldAgentOrAbove()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FarmerGroupDetailSerializer
        return FarmerGroupListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = FarmerGroup.objects.all()

        # Partners only see approved groups
        if user.role == UserRole.PARTNER_USER:
            return qs.filter(is_approved=True)

        # Field agents only see groups in their district
        if user.role == UserRole.FIELD_AGENT and user.district:
            return qs.filter(district__iexact=user.district)

        return qs

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)


class FarmerGroupDetailView(generics.RetrieveUpdateAPIView):
    queryset = FarmerGroup.objects.all()
    http_method_names = ['get', 'patch']

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsFieldAgentOrAbove()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        return FarmerGroupDetailSerializer


class ApproveGroupView(APIView):
    permission_classes = [IsSupervisorOrAbove]

    def post(self, request, pk):
        try:
            group = FarmerGroup.objects.get(pk=pk)
        except FarmerGroup.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if group.is_approved:
            return Response({'detail': 'Group is already approved.'})

        group.is_approved = True
        group.approved_by = request.user
        group.approved_at = timezone.now()
        group.save()

        # Trigger baseline impact snapshot
        from apps.impact.services import create_baseline_snapshot
        create_baseline_snapshot(group)

        return Response(FarmerGroupDetailSerializer(group).data)


class GroupLoanHistoryListCreateView(generics.ListCreateAPIView):
    serializer_class = GroupLoanHistorySerializer
    permission_classes = [IsFieldAgentOrAbove]

    def get_queryset(self):
        return GroupLoanHistory.objects.filter(group_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        group = FarmerGroup.objects.get(pk=self.kwargs['pk'])
        serializer.save(group=group)
