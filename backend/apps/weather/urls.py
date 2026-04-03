from django.urls import path
from .views import PlotWeatherView, GroupWeatherView

urlpatterns = [
    path('weather/plot/<uuid:plot_pk>/',   PlotWeatherView.as_view(),  name='weather-plot'),
    path('weather/group/<uuid:group_pk>/', GroupWeatherView.as_view(), name='weather-group'),
]
