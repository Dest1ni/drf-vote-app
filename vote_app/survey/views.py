import json
from rest_framework.views import APIView
from .serializers import CreateSurveySerializer,SurveySerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from authentication.models import User
from .models import SurveyUser

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