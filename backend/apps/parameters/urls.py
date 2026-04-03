from django.urls import path
from .views import (
    CropParameterListCreateView,
    CropParameterDetailView,
    CropIncomeIndexListView,
    CropIncomeIndexDetailView,
    LoanPolicyListCreateView,
    AuditLogListView,
)

urlpatterns = [
    path('parameters/crops/',              CropParameterListCreateView.as_view(),  name='crop-param-list'),
    path('parameters/crops/<uuid:pk>/',    CropParameterDetailView.as_view(),      name='crop-param-detail'),
    path('parameters/cii/',                CropIncomeIndexListView.as_view(),      name='cii-list'),
    path('parameters/cii/<uuid:pk>/',      CropIncomeIndexDetailView.as_view(),    name='cii-detail'),
    path('parameters/loan-policy/',        LoanPolicyListCreateView.as_view(),     name='loan-policy-list'),
    path('parameters/audit-log/',          AuditLogListView.as_view(),             name='audit-log'),
]
