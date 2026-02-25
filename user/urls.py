from django.urls import path
from .views import LoginUserAPIView, LogoutUserAPIView, RegisterUserAPIView, MeAPIView

urlpatterns = [
    path('login/', LoginUserAPIView.as_view(), name='user-login'),
    path('logout/', LogoutUserAPIView.as_view(), name='user-logout'),
    path('register/', RegisterUserAPIView.as_view(), name='user-register'),
    path('me/', MeAPIView.as_view(), name='user-me'),

]
