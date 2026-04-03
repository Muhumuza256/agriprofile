from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    CurrentUserView,
    ChangePasswordView,
    UserListCreateView,
    UserRetrieveUpdateView,
)

urlpatterns = [
    path('auth/login/',           LoginView.as_view(),           name='auth-login'),
    path('auth/refresh/',         TokenRefreshView.as_view(),    name='auth-refresh'),
    path('auth/logout/',          LogoutView.as_view(),          name='auth-logout'),
    path('auth/me/',              CurrentUserView.as_view(),     name='auth-me'),
    path('auth/change-password/', ChangePasswordView.as_view(),  name='auth-change-password'),
    path('users/',                UserListCreateView.as_view(),  name='user-list'),
    path('users/<uuid:pk>/',      UserRetrieveUpdateView.as_view(), name='user-detail'),
]
