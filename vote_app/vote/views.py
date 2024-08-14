from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView 
from .models import Vote,VoteOption,VoteUser
from authentication.models import User
from .serializers import VoteCreateSerializer, VoteOptionSerializer,VoteSerializer,VoteUpdateSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .service import option_exists, vote_exists
import json
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

class VoteCreateAPI(APIView):
    serializer_class = VoteCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self,request,*args,**kwargs):
        serializer = VoteCreateSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        
        vote = serializer.create(serializer.validated_data,request.user)
        if not vote.for_everyone:
            with transaction.atomic(): # Транзакция ЭЩКЕРЕЕЕ
                users_allowed = json.loads(request.data['users_allowed'])
                for item in users_allowed: 
                    user = User.objects.get(pk = item['user'])
                    VoteUser.objects.create(user = user, vote = vote)
        return Response(VoteSerializer(vote).data)
    

class VotePublishAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,pk):
            data = vote_exists(pk)
            if data['exists']:
                if data.who_create == request.user:
                    options = VoteOption.objects.filter(vote_model = pk).all()
                    if options.count() == 1:
                        return Response(data={'message': "Нельзя опубликовать голосование c одним выбором ответа"},status=400)
                    if options.count() == 0:
                        return Response(data={'message': "Нельзя опубликовать голосование без возможности выборов"},status=400)
                    data['vote'].published = True
                    data['vote'].save()
                    serializer = VoteSerializer(data['vote'])
                    data = serializer.data
                    return Response(data=data,status=200)
                return Response(data={'message': "Вы не имеете доступа к этому голосованию"},status=400)
            return Response(data={'message': "Введен несуществующий id"},status=400)

class VoteAddOptionAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VoteOptionSerializer

    def post(self,request,*args,**kwargs):
        data = vote_exists(id=request.data['vote_model'])
        if data['exists']:
            if data['vote'].who_create == request.user:
                serializer = VoteOptionSerializer(data = request.data)
                serializer.is_valid(raise_exception=True)
                option = serializer.save()
                return Response(data=VoteOptionSerializer(option).data,status=200)
            return Response(data={'message': "Вы не имеете доступа к этому голосованию"},status=400)
        return Response(data={'message': "Введен несуществующий id"},status=400)
    

class OptionUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VoteOptionSerializer

    def patch(self,request,pk,*args,**kwargs):
        data = option_exists(pk)
        if data['exists']:
            vote = Vote.objects.get(pk = data['option'].vote_model.pk)
            if vote.who_create == request.user:
                if vote.published == False:
                    serializer = VoteOptionSerializer(data['option'], data={'choice':request.data['choice']}, partial=True) # 
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(data = serializer.data,status=200)    
                else:
                    return Response(data={'message': "Нельзя изменить поля опубликованного голосования"},status=400)    
            else:
                return Response(data={'message': "Вы не имеете доступа к этому голосованию"},status=400)
        else:
            return Response(data={'message': "Введен несуществующий id"},status=400)                   
            
class OptionDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk,*args,**kwargs):
        data = option_exists(pk)
        if data['exists']:
            vote = Vote.objects.get(pk = data['option'].vote_model.pk)
            if vote.who_create == request.user:
                if vote.published == False:
                        data['option'].delete()
                        return Response(data={'message': "Объект удален успешно"},status=204)    
                else:
                    return Response(data={'message': "Нельзя удалять поля опубликованного голосования"},status=400)    
            else:
                return Response(data={'message': "Вы не имеете доступа к этому голосованию"},status=400)
        else:
            return Response(data={'message': "Введен несуществующий id"},status=400)
        
class VoteUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self,request,pk,*args,**kwargs):
        data = vote_exists(pk)
        if data['exists']:
            if data['vote'].who_create == request.user:
                if data['vote'].published == False:
                    serializer = VoteUpdateSerializer(data['vote'], data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(data = serializer.data,status=200)    
                else:
                    return Response(data={'message': "Нельзя изменить поля опубликованного голосования"},status=400)    
            else:
                return Response(data={'message': "Вы не имеете доступа к этому голосованию"},status=400)
        else:
            return Response(data={'message': "Введен несуществующий id"},status=400)     
                   
    def put(self,request,pk,*args,**kwargs): # Копипаст patch метода кроме Partial, мб не прав
        data = vote_exists(pk)
        if data['exists']:
            if data['vote'].who_create == request.user:
                if data['vote'].published == False:
                    serializer = VoteUpdateSerializer(data['vote'], data=request.data, partial=False)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(data = serializer.data,status=200)    
                else:
                    return Response(data={'message': "Нельзя изменить поля опубликованного голосования"},status=400)    
            else:
                return Response(data={'message': "Вы не имеете доступа к этому голосованию"},status=400)
        else:
            return Response(data={'message': "Введен несуществующий id"},status=400)        

class VoteDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk,*args,**kwargs):
        data = option_exists(pk)
        if data['exists']:
            vote = Vote.objects.get(pk = data['option'].vote_model.pk)
            if vote.who_create == request.user:
                if vote.published == False:
                        data['option'].delete()
                        return Response(data={'message': "Объект удален успешно"},status=204)    
                else:
                    return Response(data={'message': "Нельзя удалять поля опубликованного голосования"},status=400)    
            else:
                return Response(data={'message': "Вы не имеете доступа к этому голосованию"},status=400)
        else:
            return Response(data={'message': "Введен несуществующий id"},status=400)
        