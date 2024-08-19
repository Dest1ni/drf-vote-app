from django.urls import path
from .views import CreateSurveyAPI,AddSurveyQuestionAPI,AddQuestionOptionAPI,AnswerQuesionOptionAPI,PublishSurveyAPI

app_name = "survey"

urlpatterns = [
    path('api/v1/survey/create', CreateSurveyAPI.as_view(), name='survey-create'),
    path('api/v1/survey/add_question', AddSurveyQuestionAPI.as_view(), name='survey-add-question'),
    path('api/v1/survey/add_option', AddQuestionOptionAPI.as_view(), name='survey-add-option'),
    path('api/v1/survey/answer_option', AnswerQuesionOptionAPI.as_view(), name='survey-answer-option'),
    path('api/v1/survey/publish/<int:pk>', PublishSurveyAPI.as_view(), name='survey-answer-option'),
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