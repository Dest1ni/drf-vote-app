from django.urls import path
from .views import VoteViewSet,VotePublishAPI

app_name = "vote"

urlpatterns = [
    path('api/v1/vote/', VoteViewSet.as_view({'get': 'list', 'post': 'create'}), name='vote-list-create'),
    path('api/v1/vote/<int:pk>/', VoteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='vote-detail'),
    path('api/v1/vote/publish/<int:id>/', VotePublishAPI.as_view(), name='vote-publish'),
]
