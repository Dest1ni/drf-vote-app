from rest_framework import serializers
from authentication.service import user_exists
from .models import Survey,SurveyQuesiton,SurveyQuesitonOption,QuestionAnswerOption,SurveyUser
from .service import survey_exists,question_exists,option_exists, survey_user_exists
from django.db import transaction
from authentication.models import User

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
                raise serializers.ValidationError("Укажите хотябы одного пользователя которму можно пройти опрос",code=400)
            return data

    def create(self, validated_data, user):
        if "users_allowed" in validated_data:
            validated_data.pop("users_allowed")
        if Survey.objects.filter(name = validated_data['name']).exists():
            raise serializers.ValidationError("У вас уже есть опрос с таким названием",code=400)
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
        if SurveyQuesiton.objects.filter(survey_model = data['survey_model'], question = data['question']).exists():
            raise serializers.ValidationError("У вас уже есть такой вопрос в этом опросе",code=400)
        return data
    
class AddQuestionOptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SurveyQuesitonOption
        fields = "__all__"

    def validate(self, data):
        user = self.context['request'].user
        if data['question'].survey_model.who_create != user:
            raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)
        if SurveyQuesitonOption.objects.filter(question = data['question'],option = data['option']).exists():
            raise serializers.ValidationError("Вы уже добавили такой вариант ответа к этому голосованию",code=400)
        return data

class AnswerQuesionOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionAnswerOption
        fields = ('option','free_answer')

    def validate(self, data):
        if not data['option'].question.survey_model.published:
            raise serializers.ValidationError("Вам недоступен этот опрос",code=400)      
        if not self.context['request'].user == data['option'].question.survey_model.who_create and not data['option'].survey.question.survey_model.for_everyone:
            if not SurveyUser.objects.filter(vote = data['option'].vote_model,user = self.context['request'].user).exists():
                raise serializers.ValidationError("Вам недоступен этот опрос",code=400)  
        data['user'] = self.context['request'].user   
        return data

class PublishSurveySerializer(serializers.Serializer):
    def validate(self, data):
        survey = survey_exists(id = self.context['pk'])
        if not survey['exists']:
            raise serializers.ValidationError("Недопустимый id",code=400)      
        if self.context['request'].user != survey['survey'].who_create:
            raise serializers.ValidationError("Вам недоступен это опрос",code=400)
        survey['survey'].published = True
        survey['survey'].save()
        data['survey'] = survey['survey']
        return data
    
class UpdateSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('name','for_everyone','rerunable')
    
    def validate(self, data):
        survey = survey_exists(self.context['pk'])
        if not survey['exists']:
            raise serializers.ValidationError("Неверный id",code=400)    
        survey = survey['survey']
        if self.context['request'].user != survey.who_create:
            raise serializers.ValidationError("Вам недоступен это опрос",code=400)
        if survey.published:
            raise serializers.ValidationError("Нельзя изменить опубликованный опрос",code=400)  
        self.instance = survey       
        return data

class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuesiton
        fields = "__all__"

class SurveyQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuesitonOption
        fields = "__all__"

class UpdateSurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuesiton
        fields = ("question",)

    def validate(self, data):
        question = question_exists(self.context['pk'])
        if not question['exists']:
            raise serializers.ValidationError("Неверный id",code=400)
        if question['question'].survey_model.who_create != self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)    
        self.instance = question['question']
        return data
    
class UpdateSurveyQuestionOptionSerializer(serializers.Serializer):

    def validate(self, data):
        option = option_exists(self.context['pk'])
        if not option['exists']:
            raise serializers.ValidationError("Неверный id",code=400)
        if option['option'].question.survey_model.who_create != self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)
        self.instance = option['option']
        return data

class DeleteSurveySerializer(serializers.Serializer):
    
    def validate(self, data):
        survey = survey_exists(self.context['pk'])
        if not survey['exists']:
            raise serializers.ValidationError("Неверный id",code=400)
        if survey['survey'].published:
            raise serializers.ValidationError("Нельзя имзенить опублиеованный опрос",code=400)    
        if survey['survey'].who_create != self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)
        data['survey'] = survey['survey']
        return data

class DeleteSurveyQuestionSerializer(serializers.Serializer):
    def validate(self, data):
        question = question_exists(self.context['pk'])
        if not question['exists']:
            raise serializers.ValidationError("Неверный id",code=400)    
        if question['question'].survey_model.published:
            raise serializers.ValidationError("Нельзя имзенить опублиеованный опрос",code=400)    
        if question['question'].survey_model.who_create != self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)
        data['question'] = question['question']
        return data

class DeleteSurveyQuestionOptionSerializer(serializers.Serializer):
    def validate(self, data):
        option = option_exists(self.context['pk'])
        if not option['exists']:
            raise serializers.ValidationError("Неверный id",code=400)    
        if option['option'].question.survey_model.published:
            raise serializers.ValidationError("Нельзя имзенить опублиеованный опрос",code=400)    
        if option['option'].question.survey_model.who_create != self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)
        data['option'] = option['option']
        return data

class AddUserToAllowedList(serializers.Serializer):
    users_allowed = serializers.JSONField(required = True) #Отдельно не валидировал. TODO?

    def validate(self, data):
        survey = survey_exists(self.context['pk'])
        if not survey['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)
        if survey['survey'].who_create != self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к опросу",code=400)
        if survey['survey'].for_everyone:
            raise serializers.ValidationError("Нельзя добавить пользователей к публичному опросу",code=400)
        if survey['survey'].published:
            raise serializers.ValidationError("Нельзя добавить пользователей к опубликованному опросу",code=400)
        data['survey'] = survey['survey']
        return data
    
    def save(self,data, **kwargs):
        with transaction.atomic():
            for item in data['users_allowed']:
                for key,value in item.items():
                    if user_exists(value)['exists']:
                        user = User.objects.get(pk = value)
                        if SurveyUser.objects.filter(user=user,survey = data['survey']).exists():
                            continue
                        SurveyUser.objects.create(user = user,survey = data['survey'])
                    else:
                        raise serializers.ValidationError(f"Пользвателя {value} не существует",code=400)

class DeleteUserFromAllowedList(serializers.Serializer):
    
    user = serializers.IntegerField(required = True)
    def validate(self, data):
        user = user_exists(data['user'])
        if not user['exists']:
            raise serializers.ValidationError(f"Пользвателя {data['user']} не существует",code=400)   
        survey_user = survey_user_exists(self.context['pk'])
        if not survey_user['exists']:
            raise serializers.ValidationError(f"Пользователю уже не доступно голосование",code=400)
        if not survey_user['exists']:
            raise serializers.ValidationError(f"Пользователю уже не доступно голосование",code=400)
        data['vote_user'] = survey_user['vote_user']
        return data
    
    def save(self, data):
        data['vote_user'].delete()
