from rest_framework import serializers
from .models import Vote
from authentication.models import User

class VoteCreateSerializer(serializers.Serializer):
    users_allowed = serializers.CharField(required = False)
    name = serializers.CharField()
    who_create = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    question = serializers.CharField()
    published = serializers.BooleanField(default=False)
    for_everyone = serializers.BooleanField(required = True)
    rerunable = serializers.BooleanField(default=False)

    def validate(self, data):
        for_everyone = data.get('for_everyone')
        users_allowed = data.get('users_allowed', [])
        if not for_everyone and not users_allowed:
            raise serializers.ValidationError("Укажите хотябы одного пользователя которму можно пройти голосование")
        return data

class VoteExistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('name','id')