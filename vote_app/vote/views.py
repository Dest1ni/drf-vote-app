from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Vote,VoteUser
from authentication.models import User
from .serializers import VoteCreateSerializer, VoteOptionCreateSerializer,VoteSerializer,\
    VoteUpdateSerializer,VotePublishSerializer,VoteOptionUpdateSerializer,VoteOptionDeleteSerializer,VoteDeleteSerializer,VoteAnswerOptionSerializer,\
    AddUserToAllowedList
from rest_framework.response import Response
import json
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Q
from .service import vote_exists

class VoteCreateAPI(APIView):
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
    

class VotePublishAPI(APIView): # теоретически можно было бы убрать т.к есть апи для изменения голосования, но отдельный апи для публикации
    permission_classes = [IsAuthenticated] # делает лоигку публикации более гибкой

    def post(self, request, pk):
        serializer = VotePublishSerializer(data=request.data, context={"pk": pk, "request": request})
        serializer.is_valid(raise_exception=True)
        vote = serializer.validated_data['vote']
        vote.published = True
        vote.save()
        response_serializer = VoteSerializer(vote)
        return Response(data=response_serializer.data, status=200)

    
class VoteAddOptionAPI(APIView): 
    permission_classes = [IsAuthenticated]

    def post(self,request,*args,**kwargs):
        serializer = VoteOptionCreateSerializer(data = request.data,context={'pk':request.data['vote_model'],'request':request})
        serializer.is_valid(raise_exception=True)
        option = serializer.save()
        return Response(data=VoteOptionCreateSerializer(option).data,status=200)
    

class OptionUpdateAPI(APIView):  
    permission_classes = [IsAuthenticated]

    def patch(self,request,pk,*args,**kwargs):
        serializer = VoteOptionUpdateSerializer(data = request.data,context = {"pk":pk,'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data = serializer.data,status=200)                
            
class OptionDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk,*args,**kwargs):
        serializer = VoteOptionDeleteSerializer(data = request.data, context = {'pk':pk,'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['option'].delete()
        return Response(status=204)   
        
class VoteUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def update(self,request,pk,partial):
        serializer = VoteUpdateSerializer(data = request.data, context = {'request':request, "pk": pk},partial = partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data = serializer.data,status=200)     
      
    def patch(self,request,pk):
        self.update(request=request,pk=pk,partial=True)
                   
    def put(self,request,pk):
        self.update(request=request,pk=pk,partial=False)
    
class VoteDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk,*args,**kwargs):
        serializer = VoteDeleteSerializer(data = {"user":self.request.user,"vote":pk},context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['vote'].delete()
        return Response(status=204)


class VoteAnswerOptionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,pk,*args,**kwargs):
        serializer = VoteAnswerOptionSerializer(data = request.data,context = {'pk':pk,'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.create(validated_data=serializer.validated_data)
        return Response(status=204)   

class VoteListAPI(ListAPIView):
    serializer_class = VoteSerializer
    model = Vote
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        votes = Vote.objects.filter(Q(for_everyone = True) | Q(for_everyone = False, voteuser__user = self.request.user),published = True).distinct()
        return votes
    
class VoteDetailAPI(APIView): # TODO добавить вывод allowed users
    permission_classes = [IsAuthenticated]
    def get(self,request,pk):
        vote = vote_exists(id = pk)
        if not vote['exists']:
            return Response("Неверный id",status=400)
        serializer = VoteSerializer(vote['vote'])
        return Response(serializer.data,status=200)

class EditUsersAllowedList(APIView):
    
    def post(self,request,pk): # Vote pk
        serializer = AddUserToAllowedList(data = request.data,context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data,status=200)
    
    def delete(self,request,pk): # Allowed user pk
        pass
