from django.shortcuts import render
from .models import Vote
from rest_framework.views import APIView 
from .serializers import VoteSerializer
from rest_framework.response import Response


def vote_exists(id):
    try:
        vote = Vote.objects.get(id = id)
        data = {'vote':vote,'exists':True}
        return data
    except:
        return {'exists': False}