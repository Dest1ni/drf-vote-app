from django.shortcuts import render
from .models import Vote,VoteOption


def vote_exists(id):
    try:
        vote = Vote.objects.get(id = id)
        data = {'vote':vote,'exists':True}
        return data
    except:
        return {'exists': False}

def option_exists(id):
    try:
        option = VoteOption.objects.get(id = id)
        data = {'option':option,'exists':True}
        return data
    except:
        return {'exists': False}    

