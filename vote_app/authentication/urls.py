from django.urls import path
from .views import LoginAPIView, LogoutAPIView, RegisterAPIView, UserExistsAPI,UserInfoAPI

from rest_framework.authtoken import views

app_name = "users"

urlpatterns = [
    path('api/v1/user/exists/<int:id>', UserExistsAPI.as_view(), name='user-exists'),
    path('api/v1/user/register', RegisterAPIView.as_view(), name='user-register'),
    path('api/v1/user/login/', LoginAPIView.as_view(), name='login'),
    path('api/v1/user/logout/', LogoutAPIView.as_view(), name='logout'),
    path('info/', UserInfoAPI.as_view(), name='info'),
]
