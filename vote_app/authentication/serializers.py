from rest_framework import serializers
from .models import User

class UserExistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','id')