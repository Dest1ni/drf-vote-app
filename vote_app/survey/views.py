import json
from rest_framework.views import APIView
from .serializers import CreateSurveySerializer,SurveySerializer,AddSurveyQuestionSerializer,AddQuestionOptionSerializer,AnswerQuesionOptionSerializer,\
    PublishSurveySerializer,UpdateSurveySerializer,SurveyQuestionOptionSerializer,SurveyQuestionSerializer,UpdateSurveyQuestionSerializer,\
    UpdateSurveyQuestionOptionSerializer,DeleteSurveyQuestionOptionSerializer,DeleteSurveyQuestionSerializer,DeleteSurveySerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.generics import ListAPIView
from authentication.models import User
from django.db.models import Q
from .models import Survey, SurveyUser
from .service import survey_exists

#TODO нейминг классов неправильный см. Vote.views

class CreateSurveyAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = CreateSurveySerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        survey = serializer.create(serializer.validated_data,request.user)
        if not survey.for_everyone:
            with transaction.atomic(): # Транзакция ЭЩКЕРЕЕЕ
                users_allowed = json.loads(request.data['users_allowed'])
                for item in users_allowed: 
                    user = User.objects.get(pk = item['user'])
                    SurveyUser.objects.create(user = user, survey = survey)
        return Response(SurveySerializer(survey).data,status=201)

class SurveyPublishAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = PublishSurveySerializer(data = request.data)
        serializer.save()

class AddSurveyQuestionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = AddSurveyQuestionSerializer(data = request.data,context = {"request":request})
        serializer.is_valid(raise_exception=True)
        question = serializer.create(serializer.validated_data)
        return Response(AddSurveyQuestionSerializer(question).data,status=201)

class AddQuestionOptionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = AddQuestionOptionSerializer(data = request.data,context = {"request":request})
        serializer.is_valid(raise_exception=True)
        question = serializer.create(serializer.validated_data)
        return Response(AddQuestionOptionSerializer(question).data,status=201)

class AnswerQuesionOptionAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerQuesionOptionSerializer

    def post(self,request):
        serializer = AnswerQuesionOptionSerializer(data = request.data,context = {'request':request})
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()
        return Response(data = AnswerQuesionOptionSerializer(answer).data,status=201)

class PublishSurveyAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,pk):
        serializer = PublishSurveySerializer(data = request.data, context={'pk':pk,'request':request})
        serializer.is_valid(raise_exception=True)
        return Response(data = SurveySerializer(serializer.validated_data['survey']).data,status=201)

class DetailSurveyAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,pk):
        survey = survey_exists(id = pk)
        if not survey['exists']:
            return Response("Неверный id",status=400) # TODO Потом сделаем адекватно
        serializer = SurveySerializer(survey['survey'])
        return Response(serializer.data,status=200)
    
class UpdateSurveyAPI(APIView):
    permission_classes = [IsAuthenticated]

    def update(self,request,pk,partial):
        serializer = UpdateSurveySerializer(data = request.data,context = {'request':request,'pk':pk},partial = partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data,status=200)
    
    def path(self,request,pk):
        res = self.update(request=request,pk=pk,partial=True)
        return res 
    
    def put(self,request,pk):
        res = self.update(request=request,pk=pk,partial=False)
        return res

class ListSurveyAPI(ListAPIView):
    serializer_class = SurveySerializer
    model = Survey
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        surveys = Survey.objects.filter(Q(for_everyone = True) | Q(for_everyone = False, surveyuser__user = self.request.user),published = True).distinct()
        return surveys

class UpdateSurveyQuestionAPI(APIView):
    permission_classes = [IsAuthenticated] 

    def update(self,request,pk,partial):
        serializer = UpdateSurveyQuestionSerializer(data=request.data,context = {"request":request,"pk":pk},partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data = serializer.data,status=200)
    
    def put(self,request,pk):
        res = self.update(request = request,pk = pk,partial = False)
        return res
    
    def path(self,request,pk):
        res = self.update(request = request,pk = pk,partial = True)
        return res 

class UpdateSurveyQuestionOptionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def update(self,request,pk,partial):
        serializer = UpdateSurveyQuestionOptionSerializer(data=request.data,context = {"request":request,"pk":pk},partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data = serializer.data,status=200)
    
    def put(self,request,pk):
        res = self.update(request = request,pk = pk,partial = False)
        return res
    
    def path(self,request,pk):
        res = self.update(request = request,pk = pk,partial = True)
        return res 

class DeleteSurveyAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk):
        serializer = DeleteSurveySerializer(data = request.data,context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['survey'].delete()
        return Response(status=204)

class DeleteSurveyQuestionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk):
        serializer = DeleteSurveyQuestionSerializer(data = request.data,context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['question'].delete()
        return Response(status=204)

class DeleteSurveyQuestionOptionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk):
        serializer = DeleteSurveyQuestionOptionSerializer(data = request.data,context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['option'].delete()
        return Response(status=204)