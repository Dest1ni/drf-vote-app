from django.urls import path
from .views import SurveyCreateAPI,SurveyQuestionAddAPI,QuestionOptionAddAPI,QuesionOptionAnswerAPI,SurveyPublishAPI,SurveyDetailAPI,SurveyUpdateAPI,\
    SurveyListAPI,SurveyQuestionUpdateAPI,SurveyQuestionOptionUpdateAPI,SurveyDeleteAPI,SurveyQuestionDeleteAPI,SurveyQuestionOptionDeleteAPI,EditUsersAllowedList

app_name = "survey"

urlpatterns = [
    path('api/v1/survey/create', SurveyCreateAPI.as_view(), name='survey-create'),
    path('api/v1/survey/add_question', SurveyQuestionAddAPI.as_view(), name='survey-add-question'),
    path('api/v1/survey/add_option', QuestionOptionAddAPI.as_view(), name='survey-add-option'),
    path('api/v1/survey/answer_option', QuesionOptionAnswerAPI.as_view(), name='survey-answer-option'),
    path('api/v1/survey/publish/<int:pk>', SurveyPublishAPI.as_view(), name='survey-answer-option'),
    path('api/v1/survey/detail/<int:pk>', SurveyDetailAPI.as_view(), name='survey-detail'),
    path('api/v1/survey/update/<int:pk>', SurveyUpdateAPI.as_view(), name='survey-update'),
    path('api/v1/survey/list', SurveyListAPI.as_view(), name='survey-list'),
    path('api/v1/survey/update_option/<int:pk>', SurveyQuestionOptionUpdateAPI.as_view(), name='survey-update-option'),
    path('api/v1/survey/update_question/<int:pk>', SurveyQuestionUpdateAPI.as_view(), name='survey-update-question'),
    path('api/v1/survey/delete_question/<int:pk>', SurveyQuestionDeleteAPI.as_view(), name='survey-delete-question'),
    path('api/v1/survey/delete_option/<int:pk>', SurveyQuestionOptionDeleteAPI.as_view(), name='survey-delete-option'),
    path('api/v1/survey/delete_survey/<int:pk>', SurveyDeleteAPI.as_view(), name='survey-delete-survey'),
    path('api/v1/survey/allowed_users/<int:pk>', EditUsersAllowedList.as_view(), name='survey-user-update'),
]

# Пример для единообразия API
#urlpatterns = [
#    path('api/v1/vote/publish/<int:pk>', VotePublishAPI.as_view(), name='vote-publish'),
#    path('api/v1/vote/create', VoteCreateAPI.as_view(), name='vote-create'),
#    path('api/v1/vote/delete/<int:pk>', VoteDeleteAPI.as_view(), name='vote-delete'),
#    path('api/v1/vote/update/<int:pk>', VoteUpdateAPI.as_view(), name='vote-update'),
#    path('api/v1/vote/detail/<int:pk>', VoteDetailAPI.as_view(), name='vote-detail'),
#    path('api/v1/vote/add_option', VoteAddOptionAPI.as_view(), name='vote-add-option'),
#    path('api/v1/vote/list', VoteListAPI.as_view(), name='vote-list'),
#    path('api/v1/vote/update_option/<int:pk>', OptionUpdateAPI.as_view(), name='vote-update-option'),
#    path('api/v1/vote/delete_option/<int:pk>', OptionDeleteAPI.as_view(), name='vote-delete-option'),
#    path('api/v1/vote/answer_option/<int:pk>', VoteAnswerOptionAPI.as_view(), name='vote-answer-option'),
#]