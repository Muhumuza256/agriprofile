from django.urls import path
from .views import (
    FarmerScoreListView,
    FarmerLatestScoreView,
    TriggerScoreCalculationView,
    GroupScoreView,
)

urlpatterns = [
    path('farmers/<uuid:farmer_pk>/scores/',          FarmerScoreListView.as_view(),          name='farmer-scores'),
    path('farmers/<uuid:farmer_pk>/scores/latest/',   FarmerLatestScoreView.as_view(),         name='farmer-score-latest'),
    path('farmers/<uuid:farmer_pk>/scores/calculate/', TriggerScoreCalculationView.as_view(),  name='farmer-score-calculate'),
    path('groups/<uuid:group_pk>/score/',              GroupScoreView.as_view(),               name='group-score'),
]
