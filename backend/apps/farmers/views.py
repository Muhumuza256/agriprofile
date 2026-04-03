from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from shared.permissions import IsFieldAgentOrAbove, IsSupervisorOrAbove
from apps.accounts.models import UserRole
from .models import FarmerProfile, FarmerAsset, FarmerCrop
from .serializers import (
    FarmerProfileListSerializer,
    FarmerProfileDetailSerializer,
    FarmerAssetSerializer,
    FarmerCropSerializer,
)


class FarmerProfileListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsFieldAgentOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['district', 'gender', 'submission_status', 'group', 'is_active']
    search_fields = ['full_name', 'national_id', 'primary_phone']
    ordering_fields = ['created_at', 'full_name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FarmerProfileDetailSerializer
        return FarmerProfileListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = FarmerProfile.objects.select_related('group').all()
        if user.role == UserRole.FIELD_AGENT and user.district:
            return qs.filter(district__iexact=user.district)
        return qs

    def perform_create(self, serializer):
        serializer.save(field_agent=self.request.user)


class FarmerProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = FarmerProfile.objects.select_related('group', 'assets').prefetch_related('crops', 'plots')
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_serializer_class(self):
        return FarmerProfileDetailSerializer


class ApproveSubmissionView(APIView):
    permission_classes = [IsSupervisorOrAbove]

    def post(self, request, pk):
        try:
            farmer = FarmerProfile.objects.get(pk=pk)
        except FarmerProfile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        farmer.submission_status = 'approved'
        farmer.save()
        # Trigger score calculation
        from apps.scoring.tasks import calculate_farmer_score
        calculate_farmer_score.delay(str(farmer.id))
        return Response({'detail': 'Approved.', 'status': farmer.submission_status})

    def delete(self, request, pk):
        try:
            farmer = FarmerProfile.objects.get(pk=pk)
        except FarmerProfile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        farmer.submission_status = 'rejected'
        farmer.save()
        return Response({'detail': 'Rejected.', 'status': farmer.submission_status})


class FarmerCropListCreateView(generics.ListCreateAPIView):
    serializer_class = FarmerCropSerializer
    permission_classes = [IsFieldAgentOrAbove]

    def get_queryset(self):
        return FarmerCrop.objects.filter(farmer_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        farmer = FarmerProfile.objects.get(pk=self.kwargs['pk'])
        serializer.save(farmer=farmer)


class FarmerCropDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FarmerCrop.objects.all()
    serializer_class = FarmerCropSerializer
    permission_classes = [IsFieldAgentOrAbove]
    lookup_url_kwarg = 'crop_pk'


class FarmerAssetView(generics.RetrieveUpdateAPIView):
    serializer_class = FarmerAssetSerializer
    permission_classes = [IsFieldAgentOrAbove]
    http_method_names = ['get', 'put', 'patch']

    def get_object(self):
        farmer = FarmerProfile.objects.get(pk=self.kwargs['pk'])
        asset, _ = FarmerAsset.objects.get_or_create(farmer=farmer)
        return asset
