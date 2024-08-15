from rest_framework import serializers
from .models import Survey

class CreateSurveySerializer(serializers.Serializer):
    users_allowed = serializers.JSONField(required = False, 
                                          help_text="""[{id:1,user:1},{id:2, user:2}""")
    name = serializers.CharField()
    for_everyone = serializers.BooleanField(required = True)
    rerunable = serializers.BooleanField(default=False)

    def validate(self, data):
            for_everyone = data.get('for_everyone')
            users_allowed = data.get('users_allowed', [])
            if not for_everyone and not users_allowed:
                raise serializers.ValidationError("Укажите хотябы одного пользователя которму можно пройти опрос")
            return data

    def create(self, validated_data, user):
        if "users_allowed" in validated_data:
            validated_data.pop("users_allowed")
        survey = Survey.objects.create(**validated_data, who_create = user)
        return survey

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"

    