from django.urls import path
from .views import (
    PlotListCreateView,
    PlotDetailView,
    VerifyPlotView,
    FarmerPlotsView,
)

urlpatterns = [
    path('plots/',                       PlotListCreateView.as_view(),  name='plot-list'),
    path('plots/<uuid:pk>/',             PlotDetailView.as_view(),      name='plot-detail'),
    path('plots/<uuid:pk>/verify/',      VerifyPlotView.as_view(),      name='plot-verify'),
    path('farmers/<uuid:farmer_pk>/plots/', FarmerPlotsView.as_view(), name='farmer-plots'),
]
