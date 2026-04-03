from django.urls import path
from .views import (
    FarmerLoanCeilingListView,
    FarmerLoanCeilingLatestView,
    CalculateLoanCeilingView,
    GroupLoanCeilingView,
)

urlpatterns = [
    path('farmers/<uuid:farmer_pk>/loan-ceiling/',          FarmerLoanCeilingListView.as_view(),    name='farmer-loan-ceilings'),
    path('farmers/<uuid:farmer_pk>/loan-ceiling/latest/',   FarmerLoanCeilingLatestView.as_view(),  name='farmer-loan-ceiling-latest'),
    path('farmers/<uuid:farmer_pk>/loan-ceiling/calculate/', CalculateLoanCeilingView.as_view(),    name='farmer-loan-ceiling-calculate'),
    path('groups/<uuid:group_pk>/loan-ceiling/',            GroupLoanCeilingView.as_view(),         name='group-loan-ceiling'),
]
