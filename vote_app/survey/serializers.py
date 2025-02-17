from rest_framework import serializers
from authentication.service import user_exists
from .models import Survey,SurveyQuesiton,SurveyQuesitonOption,QuestionAnswerOption,SurveyUser
from .service import survey_exists,question_exists,option_exists, survey_user_exists
from django.db import transaction
from authentication.models import User
from authentication.serializers import UserSerializer
from django.db.models import Count

class CreateSurveySerializer(serializers.Serializer):
    users_allowed = serializers.JSONField(required = False)
    name = serializers.CharField(required = True,min_length = 5)
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
    
class AnswerQuestionOptionSerializer(serializers.Serializer):
    free_answer = serializers.CharField(max_length = 255,required = False)
    option = serializers.IntegerField(required = False)

    def validate(self, data):
        option = option_exists(self.context['pk'])
        if not option['exists']:
             raise serializers.ValidationError("Неверный id",code=400)    
        option = option['option']
        if not option.question.survey_model.published:
            raise serializers.ValidationError("Вам недоступен этот опрос",code=400)      
        if not self.context['request'].user == option.question.survey_model.who_create and not option.survey.question.survey_model.for_everyone:
            if not SurveyUser.objects.filter(vote = option.survey_model,user = self.context['request'].user).exists():
                raise serializers.ValidationError("Вам недоступен этот опрос",code=400)  
        if not option.question.survey_model.rerunable:
            if QuestionAnswerOption.objects.filter(option__question__survey_model=option.question.survey_model, user=self.context['request'].user):
                raise serializers.ValidationError("На этот опрос нельзя отвечать ещё раз",code=400)   
        if 'option' in data and 'free_answer' in data:
            raise serializers.ValidationError("Ответ может быть только один",code=400)          
        data['user'] = self.context['request'].user   
        data['option'] = option
        return data

    def create(self, validated_data):
        answer = QuestionAnswerOption.objects.create(**validated_data)
        return answer

class AnswerQuestionOptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswerOption
        fields = "__all__"

class PublishSurveySerializer(serializers.Serializer):
    def validate(self, data):
        survey = survey_exists(id = self.context['pk'])
        if not survey['exists']:
            raise serializers.ValidationError("Недопустимый id",code=400)      
        if self.context['request'].user != survey['survey'].who_create:
            raise serializers.ValidationError("Вам недоступен это опрос",code=400)
        questions = SurveyQuesiton.objects.filter(survey_model = survey['survey']).all()
        if questions.count() <= 1:
            raise serializers.ValidationError("Нельзя опубликовать опрос с одним или без вопросов",code=400)
        if questions.annotate(options_count=Count('surveyquesitonoption')).filter(options_count__lte = 1).count() > 0:
            raise serializers.ValidationError("Нельзя опубликовать опрос с одним или без возможностей ответа в вопросе",code=400)    
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

class SurveyQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuesitonOption
        fields = "__all__"
    
class SurveyQuestionSerializer(serializers.ModelSerializer):
    options = SurveyQuestionOptionSerializer(many=True, source='surveyquesitonoption_set')
    
    class Meta:
        model = SurveyQuesiton
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

class WatchResultSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ['id', 'name', 'who_create', 'published', 'for_everyone', 'rerunable', 'answers']

    def get_answers(self, obj):
        answers = QuestionAnswerOption.objects.filter(option__question__survey_model=obj).all()
        return AnswerQuestionOptionModelSerializer(answers, many=True).data
    
    def validate(self, data):
        survey = survey_exists(self.context['pk'])
        if not survey['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)    
        survey = survey['survey']
        if not survey.for_everyone:
            if not SurveyUser.objects.filter(survey = survey,user = self.context['request'].user).exists():
                raise serializers.ValidationError("Вы не имеете доступа к опросу",code=400)
        if survey.published == False:
            raise serializers.ValidationError("Вы не имеете доступа к опросу",code=400)    
        data['survey'] = survey
        return data

class SurveyDetailSerializer(serializers.ModelSerializer):
    allowed_users = serializers.SerializerMethodField()
    questions = SurveyQuestionSerializer(many=True, source='surveyquesiton_set')

    class Meta:
        model = Survey
        fields = "__all__"

    def get_allowed_users(self,obj):
        users = User.objects.filter(surveyuser__survey=obj)
        return UserSerializer(users, many=True).data   

    def validate(self, data):
        survey = survey_exists(self.context['pk'])
        if not survey['exists']:
            raise serializers.ValidationError("Неверный id",code=400)
        if survey['survey'].who_create != self.context['request'].user:
            if not survey['survey'].published:
                raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)    
            if not survey['survey'].for_everyone and not SurveyUser.objects.filter(survey = survey['survey'],user = self.context['request'].user).exists():
                raise serializers.ValidationError("Вы не имеете доступа к этому опросу",code=400)     
        data['survey'] = survey['survey']   
        return data