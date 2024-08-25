from rest_framework import serializers
from .models import Vote,VoteOption,VoteUser,VoteAnswer
from authentication.models import User
from .service import vote_exists,option_exists,vote_user_exists
from django.db.utils import IntegrityError
from django.db.transaction import atomic
from authentication.service import user_exists
from authentication.serializers import UserSerializer

class VoteCreateSerializer(serializers.Serializer): # Обычный сериализатор дает более гибкую логику
    users_allowed = serializers.JSONField(required = False)
    name = serializers.CharField(help_text="Название голосования")
    question = serializers.CharField(help_text="Вопрос голосования",required = True,min_length = 5)
    for_everyone = serializers.BooleanField(required = True)
    rerunable = serializers.BooleanField(default=False)

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

class VoteOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteOption
        fields = "__all__"
# Как отдавать Users_allowed в VoteDetail чтобы не нарушить логику других View не придумал поэтому отдельный сериализато
class VoteDetailSerializer(serializers.ModelSerializer): 
    allowed_users = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    class Meta:
        model = Vote
        fields = ('name','pk','question','who_create','published','for_everyone','rerunable','allowed_users','options')

    def get_allowed_users(self,obj):
        users = User.objects.filter(voteuser__vote=obj)
        return UserSerializer(users, many=True).data

    def get_options(self,obj):
            options = VoteOption.objects.filter(vote_model=obj)
            return VoteOptionSerializer(options, many=True).data

    def validate(self, data):
        vote = vote_exists(self.context['pk'])
        if not vote['exists']:
            raise serializers.ValidationError("Неверный id",code=400)
        if vote['vote'].who_create != self.context['request'].user:
            if not vote['vote'].published:
                raise serializers.ValidationError("Вы не имеете доступа к этому голосованию",code=400)    
            if not vote['vote'].for_everyone and not VoteUser.objects.filter(vote = vote['vote'],user = self.context['request'].user).exists():
                raise serializers.ValidationError("Вы не имеете доступа к этому голосованию",code=400)     
        data['vote'] = vote['vote']   
        return data
    
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
        if vote['vote'].published:
            raise serializers.ValidationError("Нельзя добавить вариант ответа к опубликованному голосованию",code=400)
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
        if option['option'].vote_model.published:
            raise serializers.ValidationError("Нельзя изменить вариант ответа опубликованного голосования",code=400)
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
        if not vote['exists']:
            raise serializers.ValidationError("Введен несуществующий id")    
        if not vote['vote'].who_create == self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к этому голосованию")
        options = VoteOption.objects.filter(vote_model=id).all()
        if options.count() == 1:
            raise serializers.ValidationError("Нельзя опубликовать голосование c одним выбором ответа")
        if options.count() == 0:
            raise serializers.ValidationError("Нельзя опубликовать голосование без возможности выборов")
        data['vote'] = vote['vote']
        return data
            
        

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

class ResultsAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteAnswer
        fields = '__all__'

class AddUserToAllowedList(serializers.Serializer):
    users_allowed = serializers.JSONField(required = True)

    def validate(self, data):
        vote = vote_exists(self.context['pk'])
        if not vote['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)
        if vote['vote'].who_create != self.context['request'].user:
            raise serializers.ValidationError("Вы не имеете доступа к голосованию",code=400)
        if vote['vote'].for_everyone:
            raise serializers.ValidationError("Нельзя добавить пользователей к публичному голосованию",code=400)
        if vote['vote'].for_everyone:
            raise serializers.ValidationError("Нельзя добавить пользователей к опубликованному голосованию",code=400)
        data['vote'] = vote['vote']
        print(data['users_allowed'])
        return data
    
    def save(self,data, **kwargs):
        item = data['users_allowed']
        print(item)
        with atomic():
            for key,value in item.items():
                if user_exists(value)['exists']:
                    user = User.objects.get(pk = value)
                    if VoteUser.objects.filter(user=user,vote = data['vote']).exists():
                        continue
                    VoteUser.objects.create(user = user,vote = data['vote'])
                else:
                    raise serializers.ValidationError(f"Пользвателя {value} не существует",code=400)

class DeleteUserFromAllowedList(serializers.Serializer):
    
    user = serializers.IntegerField(required = True)
    def validate(self, data):
        user = user_exists(data['user'])
        if not user['exists']:
            raise serializers.ValidationError(f"Пользвателя {data['user']} не существует",code=400)   
        vote_user = vote_user_exists(user_id = user['user'].id, vote_id = self.context['pk'])
        if not vote_user['exists']:
            raise serializers.ValidationError(f"Пользователю уже не доступно голосование",code=400)
        if not vote_user['exists']:
            raise serializers.ValidationError(f"Пользователю уже не доступно голосование",code=400)
        data['vote_user'] = vote_user['vote_user']
        return data
    
    def save(self, data):
        data['vote_user'].delete()

class WatchResultSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = ['id', 'name', 'who_create', 'published', 'for_everyone', 'rerunable', 'answers']

    def get_answers(self, obj):
        answers = VoteAnswer.objects.filter(option__vote_model=obj).all()
        return ResultsAnswersSerializer(answers,many = True).data
    
    def validate(self, data):
        vote = vote_exists(self.context['pk'])
        if not vote['exists']:
            raise serializers.ValidationError("Введен несуществующий id",code=400)    
        vote = vote['vote']
        if not vote.for_everyone:
            if (not VoteUser.objects.filter(vote = vote,user = self.context['request'].user).exists() )and vote.who_create != self.context['request'].user:
                raise serializers.ValidationError("Вы не имеете доступа к голосованию",code=400)
        print(vote)
        if vote.published == False:
            raise serializers.ValidationError("Голосовое не опубликовано",code=400)    
        data['vote'] = vote
        return data


