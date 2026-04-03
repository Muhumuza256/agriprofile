from django.urls import path
from .views import (
    FarmerCreditReportView,
    GroupCreditReportView,
    CropIntelligenceExportView,
    UnbankedFarmersExportView,
)

urlpatterns = [
    path('reports/farmer-credit/<uuid:farmer_id>/',  FarmerCreditReportView.as_view(),      name='report-farmer-credit'),
    path('reports/group-credit/<uuid:group_id>/',    GroupCreditReportView.as_view(),        name='report-group-credit'),
    path('reports/crop-intelligence/export/',        CropIntelligenceExportView.as_view(),   name='report-crop-excel'),
    path('reports/unbanked-farmers/export/',         UnbankedFarmersExportView.as_view(),    name='report-unbanked'),
]
