from django.shortcuts import render
from .models import User
from rest_framework.views import APIView 
from .serializers import LoginSerializer, UserExistsSerializer, UserRegistrationSerializer
from rest_framework.response import Response
from .service import user_exists
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated


class UserInfoAPI(APIView):

    def post(self,request):
        print(request.user)
        return Response({'info': UserExistsSerializer(self.request.user).data})

class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token,created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
        }, status= 201)

class LoginAPIView(APIView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
        }, status= 200)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out'}, status=200)
        except AttributeError:
            return Response({'detail': 'Token does not exist or is invalid.'}, status=401)