import json
from rest_framework.views import APIView
from .serializers import CreateSurveySerializer, SurveyDetailSerializer,SurveySerializer,AddSurveyQuestionSerializer,AddQuestionOptionSerializer,AnswerQuestionOptionSerializer,\
    PublishSurveySerializer,UpdateSurveySerializer,UpdateSurveyQuestionSerializer,\
    UpdateSurveyQuestionOptionSerializer,DeleteSurveyQuestionOptionSerializer,DeleteSurveyQuestionSerializer,\
    DeleteSurveySerializer,DeleteUserFromAllowedList,AddUserToAllowedList, AnswerQuestionOptionModelSerializer,WatchResultSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.generics import ListAPIView
from authentication.models import User
from django.db.models import Q
from .models import Survey, SurveyUser
from .service import survey_exists


class SurveyCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = CreateSurveySerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        survey = serializer.create(serializer.validated_data,request.user)
        if not survey.for_everyone:
            with transaction.atomic():
                users_allowed = json.loads(request.data['users_allowed'])
                for item in users_allowed: 
                    user = User.objects.get(pk = item['user'])
                    SurveyUser.objects.create(user = user, survey = survey)
        return Response(SurveySerializer(survey).data,status=201)


class SurveyQuestionAddAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = AddSurveyQuestionSerializer(data = request.data,context = {"request":request})
        serializer.is_valid(raise_exception=True)
        question = serializer.create(serializer.validated_data)
        return Response(AddSurveyQuestionSerializer(question).data,status=201)

class QuestionOptionAddAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = AddQuestionOptionSerializer(data = request.data,context = {"request":request})
        serializer.is_valid(raise_exception=True)
        question = serializer.create(serializer.validated_data)
        return Response(AddQuestionOptionSerializer(question).data,status=201)

class QuesionOptionAnswerAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,pk):
        serializer = AnswerQuestionOptionSerializer(data = request.data,context = {'request':request,'pk':pk})
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()
        print(answer)
        return Response(data = AnswerQuestionOptionModelSerializer(answer).data,status=201)

class SurveyPublishAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,pk):
        serializer = PublishSurveySerializer(data = request.data, context={'pk':pk,'request':request})
        serializer.is_valid(raise_exception=True)
        return Response(data = SurveySerializer(serializer.validated_data['survey']).data,status=201)

class SurveyDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,pk):
        survey = survey_exists(id = pk)
        if not survey['exists']:
            return Response("Неверный id",status=400)
        serializer = SurveyDetailSerializer(survey['survey'],context = {"request":request,"pk":pk})
        serializer.validate(serializer.data)
        return Response(serializer.data,status=200)
    
class SurveyUpdateAPI(APIView):
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

class SurveyListAPI(ListAPIView):
    serializer_class = SurveySerializer
    model = Survey
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        surveys = Survey.objects.filter(Q(for_everyone = True) | Q(for_everyone = False, surveyuser__user = self.request.user),published = True).distinct()
        return surveys

class SurveyQuestionUpdateAPI(APIView):
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

class SurveyQuestionOptionUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def update(self,request,pk,partial):
        serializer = UpdateSurveyQuestionOptionSerializer(data=request.data,context = {"request":request,"pk":pk},partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data = serializer.data,status=200)
    
    def put(self,request,pk):
        return self.update(request = request,pk = pk,partial = False)
         
    
    def path(self,request,pk):
        return self.update(request = request,pk = pk,partial = True)

class SurveyDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk):
        serializer = DeleteSurveySerializer(data = request.data,context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['survey'].delete()
        return Response(status=204)

class SurveyQuestionDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk):
        serializer = DeleteSurveyQuestionSerializer(data = request.data,context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['question'].delete()
        return Response(status=204)

class SurveyQuestionOptionDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,pk):
        serializer = DeleteSurveyQuestionOptionSerializer(data = request.data,context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['option'].delete()
        return Response(status=204)

class EditUsersAllowedList(APIView): # В случае с post сериализатор ждет список жсонов, в случае с delete ждет просто int мб плохая практика
    
    def post(self,request,pk): # Vote pk
        serializer = AddUserToAllowedList(data = request.data,context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.save(data = serializer.validated_data)
        return Response(data=serializer.data,status=200)
    
    def delete(self,request,pk): # Vote pk 
        serializer = DeleteUserFromAllowedList(data = request.data,context = {"pk":pk,"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.save(data = serializer.validated_data)
        return Response(status=204)

class WatchResults(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        survey = survey_exists(pk) # Эти 3 строчки должны быть быть в методе validate как их туда запихнуть не придумал
        if not survey['exists']:
            return Response("Неверный id", status=400)
        serializer = WatchResultSerializer(instance=survey['survey'], context={"request": request, "pk": pk})
        serializer.validate(serializer.data)
        return Response(serializer.data, status=200)
