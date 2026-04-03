from rest_framework import generics
from rest_framework.response import Response
from shared.permissions import IsSystemAdmin, IsAnalystOrAbove
from .models import CropParameter, CropIncomeIndex, LoanPolicyParameter, ParameterAuditLog
from .serializers import (
    CropParameterSerializer, CropIncomeIndexSerializer,
    LoanPolicyParameterSerializer, ParameterAuditLogSerializer,
)


class CropParameterListCreateView(generics.ListCreateAPIView):
    queryset = CropParameter.objects.filter(is_active=True)
    serializer_class = CropParameterSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSystemAdmin()]
        return [IsAnalystOrAbove()]

    def perform_create(self, serializer):
        serializer.save(last_updated_by=self.request.user)


class CropParameterDetailView(generics.RetrieveUpdateAPIView):
    queryset = CropParameter.objects.all()
    serializer_class = CropParameterSerializer
    http_method_names = ['get', 'patch']

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsSystemAdmin()]
        return [IsAnalystOrAbove()]

    def perform_update(self, serializer):
        old_instance = self.get_object()
        # Log each changed field
        for field, new_val in serializer.validated_data.items():
            old_val = getattr(old_instance, field)
            if str(old_val) != str(new_val):
                ParameterAuditLog.objects.create(
                    parameter_model='CropParameter',
                    parameter_id=old_instance.id,
                    field_changed=field,
                    old_value=str(old_val),
                    new_value=str(new_val),
                    changed_by=self.request.user,
                )
        instance = serializer.save(last_updated_by=self.request.user)
        # Queue score recalculation
        from apps.scoring.tasks import recalculate_all_scores
        recalculate_all_scores.delay()


class CropIncomeIndexListView(generics.ListCreateAPIView):
    queryset = CropIncomeIndex.objects.filter(is_active=True)
    serializer_class = CropIncomeIndexSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSystemAdmin()]
        return [IsAnalystOrAbove()]


class CropIncomeIndexDetailView(generics.RetrieveUpdateAPIView):
    queryset = CropIncomeIndex.objects.all()
    serializer_class = CropIncomeIndexSerializer
    http_method_names = ['get', 'patch']

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsSystemAdmin()]
        return [IsAnalystOrAbove()]


class LoanPolicyListCreateView(generics.ListCreateAPIView):
    queryset = LoanPolicyParameter.objects.filter(is_active=True)
    serializer_class = LoanPolicyParameterSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSystemAdmin()]
        return [IsAnalystOrAbove()]


class AuditLogListView(generics.ListAPIView):
    queryset = ParameterAuditLog.objects.all().order_by('-created_at')
    serializer_class = ParameterAuditLogSerializer
    permission_classes = [IsSystemAdmin]
