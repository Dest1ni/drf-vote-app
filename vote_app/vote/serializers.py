from rest_framework import serializers
from .models import Vote,VoteOption,VoteUser,VoteAnswer
from authentication.models import User
from .service import vote_exists,option_exists
from django.db.utils import IntegrityError

class VoteCreateSerializer(serializers.Serializer): # Обычный сериализатор дает более гибкую логику
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
            raise serializers.ValidationError("Укажите хотябы одного пользователя которму можно пройти голосование",code=400)
        return data
    
    def create(self, validated_data, user):
        if "users_allowed" in validated_data:
            validated_data.pop("users_allowed") 
        try:
            vote = Vote.objects.create(**validated_data, who_create = user)
        except IntegrityError:
            raise serializers.ValidationError("У вас уже сущетсвует голсование с таким названием",code=400)
        return vote
    

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('name','pk','question','who_create','published','for_everyone','rerunable')

class VoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('name','question','published','for_everyone','rerunable')
    
    def validate(self, data):
        vote = vote_exists(self.context['pk'])
        if not vote['exists']:
            raise serializers.ValidationError("Введен несуществующий id", code=400)
        if not vote['vote'].who_create == self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому голосованию", code=400)
        if not vote['vote'].published == False:
            raise serializers.ValidationError("Нельзя изменить поля опубликованного голосования", code=400)
        self.instance = vote['vote']
        return data

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except IntegrityError:
            raise serializers.ValidationError("У вас уже есть голосование с таким названием", code=400)
        
class VoteExistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('name','pk')

class VoteOptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteOption
        fields = ('choice','vote_model')
    
    def validate(self, data):
        vote = vote_exists(self.context['pk'])
        if not vote['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)
        if not vote['vote'].who_create == self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому голосованию",code=400)
        return data

class VoteOptionUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = VoteOption
        fields = ('choice',)

    def validate(self, data):
        option = option_exists(self.context['pk'])
        if not option['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)
        if not option['option'].vote_model.who_create == self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому голосованию",code=400)
        self.instance = option['option'] 
        return data   
    
    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except IntegrityError:
            raise serializers.ValidationError("У вас уже есть такой вариант ответа в этом голосовании",code=400)
class VoteOptionDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = VoteOption
        fields = ('pk',)

    def validate(self, data):
        option = option_exists(self.context['pk'])
        if not option['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)
        if not option['option'].vote_model.who_create == self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому голосованию",code=400)
        if option['option'].vote_model.published == True:
            raise serializers.ValidationError("Нельзя удалить поля опубликованного голосования",code=400)   
        data['option'] = option['option'] 
        return data
        
class VotePublishSerializer(serializers.Serializer):
    def validate(self, data):
        id = self.context['pk']
        vote = vote_exists(id)
        if vote['exists']:
            if vote['vote'].who_create == self.context['request'].user:
                options = VoteOption.objects.filter(vote_model=id).all()
                if options.count() == 1:
                    raise serializers.ValidationError("Нельзя опубликовать голосование c одним выбором ответа")
                if options.count() == 0:
                    raise serializers.ValidationError("Нельзя опубликовать голосование без возможности выборов")
                data['vote'] = vote['vote']
                return data
            raise serializers.ValidationError("Вы не имеете доступа к этому голосованию")
        raise serializers.ValidationError("Введен несуществующий id")

class VoteDeleteSerializer(serializers.Serializer):
    def validate(self,data):
        vote = vote_exists(self.context['pk'])
        if not vote['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)
        if not vote['vote'].who_create == self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому голосованию",code=400)
        data['vote'] = vote['vote']
        return data

class VoteAnswerOptionSerializer(serializers.Serializer):
    def validate(self, data):
        option = option_exists(self.context['pk'])
        if not option['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)
        if not self.context['request'].user == option['option'].vote_model.who_create and not option['option'].vote_model.for_everyone:
            if not VoteUser.objects.filter(vote = option['option'].vote_model,user = self.context['request'].user).exists():
                raise serializers.ValidationError("Вам недоступно это голосование",code=400)
        if VoteAnswer.objects.filter(option__vote_model=option['option'].vote_model, user=self.context['request'].user).exists():
            raise serializers.ValidationError("Вы уже ответили на это голосование",code=400)
        if not option['option'].vote_model.published:
            raise serializers.ValidationError("Вы пытаетесь ответить на не опубликованное голосование",code=400)
        data['option'] = option['option']
        data['user'] = self.context['request'].user
        return data
    
    def create(self, validated_data):
        try:
            VoteAnswer.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError("Вы уже ответили на это голосование",code=400)

class AddUserToAllowedList(serializers.Serializer):
    user_allowed = serializers.JSONField(required = True) #Отдельно не валидировал. TODO?

    def validate(self, data):
        vote = vote_exists(self.context['pk'])
        if not vote['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)
        if vote['vote'].who_create != self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к голосованию",code=400)
        return data
    
    def save(self, **kwargs):
        print(**kwargs)

class DeleteUserFromAllowedList(serializers.Serializer):
    
    def validate(self, data):
        return data
    
    def save(self, **kwargs):

        return super().save(**kwargs)

