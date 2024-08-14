from rest_framework import serializers
from .models import Vote,VoteOption
from authentication.models import User


class VoteCreateSerializer(serializers.Serializer):
    users_allowed = serializers.JSONField(required = False, 
                                          help_text="""[
                                          {
                                            id:1,
                                            user:1 # id Юзера
                                          },
                                          {
                                            id:2,
                                            user:2 # id Юзера
                                          }
                                          ]"""
                                          )
    name = serializers.CharField(help_text="Название голосования")
    question = serializers.CharField(help_text="Вопрос голосования")
    for_everyone = serializers.BooleanField(required = True)
    rerunable = serializers.BooleanField(default=False,help_text="Флаг перепроходимости голосования")

    def validate(self, data):
        for_everyone = data.get('for_everyone')
        users_allowed = data.get('users_allowed', [])
        if not for_everyone and not users_allowed:
            raise serializers.ValidationError("Укажите хотябы одного пользователя которму можно пройти голосование")
        return data
    
    def create(self, validated_data, user):
        if "users_allowed" in validated_data:
            validated_data.pop("users_allowed")
        vote = Vote.objects.create(**validated_data, who_create = user)
        return vote
    

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('name','pk','question','who_create','published','for_everyone','rerunable')

class VoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('name','question','published','for_everyone','rerunable')

class VoteExistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('name','pk')

class VoteOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteOption
        fields = ('choice','vote_model','pk')