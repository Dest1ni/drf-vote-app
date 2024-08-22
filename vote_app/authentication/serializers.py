from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class UserExistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','id')

class UserSerializer(serializers.ModelSerializer): # Пока копипаст
    class Meta:
        model = User
        fields = ('username','id')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)
    password = serializers.CharField(required = True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        print(user)
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        return {'user': user}