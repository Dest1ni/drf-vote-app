from django.urls import path
from .views import CreateSurveyAPI,AddSurveyQuestionAPI,AddQuestionOptionAPI,AnswerQuesionOptionAPI,PublishSurveyAPI,DetailSurveyAPI,UpdateSurveyAPI,\
    ListSurveyAPI,UpdateSurveyQuestionAPI,UpdateSurveyQuestionOptionAPI,DeleteSurveyAPI,DeleteSurveyQuestionAPI,DeleteSurveyQuestionOptionAPI

app_name = "survey"

urlpatterns = [
    path('api/v1/survey/create', CreateSurveyAPI.as_view(), name='survey-create'),
    path('api/v1/survey/add_question', AddSurveyQuestionAPI.as_view(), name='survey-add-question'),
    path('api/v1/survey/add_option', AddQuestionOptionAPI.as_view(), name='survey-add-option'),
    path('api/v1/survey/answer_option', AnswerQuesionOptionAPI.as_view(), name='survey-answer-option'),
    path('api/v1/survey/publish/<int:pk>', PublishSurveyAPI.as_view(), name='survey-answer-option'),
    path('api/v1/survey/detail/<int:pk>', DetailSurveyAPI.as_view(), name='survey-detail'),
    path('api/v1/survey/update/<int:pk>', UpdateSurveyAPI.as_view(), name='survey-update'),
    path('api/v1/survey/list', ListSurveyAPI.as_view(), name='survey-list'),
    path('api/v1/survey/update_option/<int:pk>', UpdateSurveyQuestionOptionAPI.as_view(), name='survey-update-option'),
    path('api/v1/survey/update_question/<int:pk>', UpdateSurveyQuestionAPI.as_view(), name='survey-delete-question'),
    path('api/v1/survey/delete_question/<int:pk>', DeleteSurveyQuestionAPI.as_view(), name='survey-delete-question'),
    path('api/v1/survey/delete_option/<int:pk>', DeleteSurveyQuestionOptionAPI.as_view(), name='survey-delete-question'),
    path('api/v1/survey/delete_survey/<int:pk>', DeleteSurveyAPI.as_view(), name='survey-delete-question'),
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