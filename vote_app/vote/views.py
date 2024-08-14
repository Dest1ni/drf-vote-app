from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView 
from .models import Vote,VoteOption,VoteUser
from authentication.models import User
from .serializers import VoteCreateSerializer, VoteOptionCreateSerializer,VoteSerializer,\
    VoteUpdateSerializer,VotePublishSerializer,VoteOptionUpdateSerializer,VoteOptionDeleteSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .service import option_exists, vote_exists
import json
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

class VoteCreateAPI(APIView): # Перенес валидацию
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
    

class VotePublishAPI(APIView): # Перенес валидацию
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = VotePublishSerializer(data=request.data, context={"id": pk, "request": request})
        serializer.is_valid(raise_exception=True)
        vote = serializer.validated_data['vote']
        vote.published = True
        vote.save()
        response_serializer = VoteSerializer(vote)
        return Response(data=response_serializer.data, status=200)

    
class VoteAddOptionAPI(APIView): # Перенес валидацию
    permission_classes = [IsAuthenticated]
    serializer_class = VoteOptionCreateSerializer

    def post(self,request,*args,**kwargs):
        serializer = VoteOptionCreateSerializer(data = request.data,context={'id':request.data['vote_model'],'request':request})
        serializer.is_valid(raise_exception=True)
        option = serializer.save()
        return Response(data=VoteOptionCreateSerializer(option).data,status=200)
    

class OptionUpdateAPI(APIView):  # Перенес валидацию
    permission_classes = [IsAuthenticated]
    serializer_class = VoteOptionUpdateSerializer

    def patch(self,request,pk,*args,**kwargs):
        serializer = VoteOptionUpdateSerializer(data = request.data,context = {"id":pk,'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data = serializer.data,status=200)                
            
class OptionDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk,*args,**kwargs):
        serializer = VoteOptionDeleteSerializer(data = request.data, context = {'id':pk,'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['option'].delete()
        return Response(status=204)   
        
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
        