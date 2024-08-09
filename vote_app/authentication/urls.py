from django.urls import path
from .views import UserExistsAPI


app_name = "users"

urlpatterns = [
    path('api/v1/user/exists/<int:id>', UserExistsAPI.as_view(), name='user-exists'),
]
