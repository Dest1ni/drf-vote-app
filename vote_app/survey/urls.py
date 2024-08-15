from django.urls import path
from .views import CreateSurveyAPI
app_name = "survey"

urlpatterns = [
    path('api/v1/survey/create', CreateSurveyAPI.as_view(), name='survey-create'),
]
