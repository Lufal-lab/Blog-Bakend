from django.urls import path
from .views import LoginUserAPIView, LogoutUserAPIView, RegisterUserAPIView

"""
URL configuration for the 'users' app.

Defines endpoints for user authentication and registration:
- login/    : User login endpoint
- logout/   : User logout endpoint
- register/ : User registration endpoint
"""

urlpatterns = [
    path('login/', LoginUserAPIView.as_view(), name='user-login'),
    path('logout/', LogoutUserAPIView.as_view(), name='user-logout'),
    path('register/', RegisterUserAPIView.as_view(), name='user-register'),
]
