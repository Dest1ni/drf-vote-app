from rest_framework import serializers
from .models import Survey,SurveyQuesiton,SurveyQuesitonOption,QuestionAnswerOption,SurveyUser
from .service import survey_exists

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

class AddSurveyQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurveyQuesiton
        fields = "__all__"

    def validate(self, data):
        user = self.context['request'].user
        if data['survey_model'].who_create != user:
            raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)
        #survey = survey_exists(self.context['request'][]) ModelSerializer сразу проверяет на существование объекта
        return data
    
class AddQuestionOptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SurveyQuesitonOption
        fields = "__all__"

    def validate(self, data):
        user = self.context['request'].user
        if data['question'].survey_model.who_create != user:
            raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)
        return data

class AnswerQuesionOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionAnswerOption
        fields = ('option','free_answer','user')

    def validate(self, data):
        if not self.context['request'].user == data['option'].question.survey_model.who_create and not data['option'].survey.question.survey_model.for_everyone:
            if not SurveyUser.objects.filter(vote = data['option'].vote_model,user = self.context['request'].user).exists():
                raise serializers.ValidationError("Вам недоступно это голосование",code=400)  
        if self.context['request'].user != data['user']:
                raise serializers.ValidationError("Ошибка пользователя",code=400)  
        data['user'] = self.context['request'].user   
        return data