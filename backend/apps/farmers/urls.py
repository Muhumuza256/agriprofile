from django.urls import path
from .views import (
    FarmerProfileListCreateView,
    FarmerProfileDetailView,
    ApproveSubmissionView,
    FarmerCropListCreateView,
    FarmerCropDetailView,
    FarmerAssetView,
)

urlpatterns = [
    path('farmers/',                              FarmerProfileListCreateView.as_view(), name='farmer-list'),
    path('farmers/<uuid:pk>/',                    FarmerProfileDetailView.as_view(),     name='farmer-detail'),
    path('farmers/<uuid:pk>/approve/',            ApproveSubmissionView.as_view(),       name='farmer-approve'),
    path('farmers/<uuid:pk>/crops/',              FarmerCropListCreateView.as_view(),    name='farmer-crops'),
    path('farmers/<uuid:pk>/crops/<uuid:crop_pk>/', FarmerCropDetailView.as_view(),     name='farmer-crop-detail'),
    path('farmers/<uuid:pk>/assets/',             FarmerAssetView.as_view(),             name='farmer-assets'),
]
