from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView 
from .models import Vote,VoteOption
from .serializers import VoteCreateSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .service import vote_exists

class VoteViewSet(ModelViewSet):
    model = Vote
    #serializer_class = VoteSerializer

    def get_queryset(self):
        return Vote.objects.filter(published = True).all()
    
    def list(self,request,*args,**kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Полное обновление существующего объекта модели.
        """
        partial = False
        print(request.data)
        instance = Vote.objects.get()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление существующего объекта модели.
        """
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        return Response(status=200)
    
class VoteCreateAPI(APIView):
    serializer_class = VoteCreateSerializer

class VotePublishAPI(APIView):
    def post(self,request,id):
        data = vote_exists(id=id)
        if data['exists']:
            options = VoteOption.objects.filter(vote_model = id).all()
            if options.count() == 1:
                return Response(data={'message': "Нельзя опубликовать голосование c одним выбором ответа"},status=400)
            if options.count() == 0:
                return Response(data={'message': "Нельзя опубликовать голосование без возможности выборов"},status=400)
            data['vote'].published = True
            data['vote'].save()
            serializer = VoteSerializer(data['vote'])
            data = serializer.data
            return Response(data=data,status=200)
        return Response(data={'message': "Введен несуществующий id"},status=400)