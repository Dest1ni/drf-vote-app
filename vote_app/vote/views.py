from rest_framework import generics
from .models import Vote
from .serializers import VoteSerializer


class VoteAPIView(generics.ListAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer