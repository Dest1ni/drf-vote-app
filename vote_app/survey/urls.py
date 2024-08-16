from django.urls import path
from .views import CreateSurveyAPI,AddSurveyQuestionAPI,AddQuestionOptionAPI,AnswerQuesionOptionAPI

app_name = "survey"

urlpatterns = [
    path('api/v1/survey/create', CreateSurveyAPI.as_view(), name='survey-create'),
    path('api/v1/survey/add_question', AddSurveyQuestionAPI.as_view(), name='survey-add-question'),
    path('api/v1/survey/add_option', AddQuestionOptionAPI.as_view(), name='survey-add-option'),
    path('api/v1/survey/answer_option', AnswerQuesionOptionAPI.as_view(), name='survey-answer-option'),
]
