from django.urls import path
from .views import (
    FarmerGroupListCreateView,
    FarmerGroupDetailView,
    ApproveGroupView,
    GroupLoanHistoryListCreateView,
)

urlpatterns = [
    path('groups/',                         FarmerGroupListCreateView.as_view(),     name='group-list'),
    path('groups/<uuid:pk>/',               FarmerGroupDetailView.as_view(),         name='group-detail'),
    path('groups/<uuid:pk>/approve/',       ApproveGroupView.as_view(),              name='group-approve'),
    path('groups/<uuid:pk>/loan-history/',  GroupLoanHistoryListCreateView.as_view(), name='group-loan-history'),
]
