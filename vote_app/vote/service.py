from django.shortcuts import render
from .models import Vote,VoteOption,VoteUser


def vote_exists(id:int) -> dict:
    """
    Проверяет голосование на существование 
    """
    try:
        vote = Vote.objects.get(id = id)
        data = {'vote':vote,'exists':True}
        return data
    except:
        return {'exists': False}

def option_exists(id:int) -> dict:
    """
    Проверяет вариант ответа на существование 
    """
    try:
        option = VoteOption.objects.get(id = id)
        data = {'option':option,'exists':True}
        return data
    except:
        return {'exists': False}    

def vote_user_exists(id:int) -> dict:
    """
    Проверяет разрешение юзера на существование 
    """
    try:
        vote_user = VoteUser.objects.get(id = id)
        data = {'vote_user':vote_user,'exists':True}
        return data
    except:
        return {'exists': False}    


