from django.urls import path
from .views import FarmerCalendarView, GroupCalendarView, GenerateSeasonCalendarView

urlpatterns = [
    path('calendar/farmer/<uuid:farmer_pk>/',          FarmerCalendarView.as_view(),          name='farmer-calendar'),
    path('calendar/group/<uuid:group_pk>/',             GroupCalendarView.as_view(),            name='group-calendar'),
    path('calendar/farmer/<uuid:farmer_pk>/generate/', GenerateSeasonCalendarView.as_view(),   name='generate-calendar'),
]
