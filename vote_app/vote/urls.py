from django.urls import path
from .views import VoteAPIView

app_name = "vote"

urlpatterns = [
    path('api/v1/vote/',VoteAPIView.as_view(),name = "vote-create"),
]