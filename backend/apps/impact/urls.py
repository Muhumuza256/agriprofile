from django.urls import path
from .views import GroupSnapshotListCreateView, GroupComparisonView, RefreshBaselineView

urlpatterns = [
    path('groups/<uuid:group_pk>/impact/',            GroupSnapshotListCreateView.as_view(), name='group-impact'),
    path('groups/<uuid:group_pk>/impact/comparison/', GroupComparisonView.as_view(),          name='group-comparison'),
    path('groups/<uuid:group_pk>/impact/baseline/',   RefreshBaselineView.as_view(),          name='group-baseline'),
]
