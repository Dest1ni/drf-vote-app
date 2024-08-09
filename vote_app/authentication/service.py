from django.shortcuts import render
from .models import User
from rest_framework.views import APIView 
from .serializers import UserExistsSerializer
from rest_framework.response import Response


def user_exists(id):
    try:
        user = User.objects.get(id = id)
        data = {'user':user,'exists':True}
        return data
    except:
        return {'exists': False}