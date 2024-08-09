from django.shortcuts import render
from .models import User
from rest_framework.views import APIView 
from .serializers import UserExistsSerializer
from rest_framework.response import Response
from .service import user_exists


class UserExistsAPI(APIView):
    def get(self,request,id):
        data = user_exists(id)
        if data['exists']:
            data['user'] = UserExistsSerializer(data['user']).data
            return Response(data=data)
        return Response({'exists': False})