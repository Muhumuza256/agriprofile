from django.urls import path
from .views import (
    OverviewView,
    ScoreDistributionView,
    CropIntelligenceView,
    SeasonalWindowsView,
    DistrictProfileView,
    AgentPerformanceView,
    ImpactSummaryView,
    GroupMapView,
)

urlpatterns = [
    path('analytics/overview/',                    OverviewView.as_view(),          name='analytics-overview'),
    path('analytics/score-distribution/',          ScoreDistributionView.as_view(), name='analytics-score-dist'),
    path('analytics/crop-intelligence/',           CropIntelligenceView.as_view(),  name='analytics-crops'),
    path('analytics/seasonal-windows/',            SeasonalWindowsView.as_view(),   name='analytics-seasonal'),
    path('analytics/district/<str:district>/',     DistrictProfileView.as_view(),   name='analytics-district'),
    path('analytics/agent-performance/',           AgentPerformanceView.as_view(),  name='analytics-agents'),
    path('analytics/impact-summary/',              ImpactSummaryView.as_view(),     name='analytics-impact'),
    path('analytics/groups/map/',                  GroupMapView.as_view(),          name='analytics-map'),
]
