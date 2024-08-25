from typing import Iterable
from django.db import models
from authentication.models import User
from django.core.exceptions import ValidationError
from rest_framework.response import Response

class Survey(models.Model):
    """
    Модель опроса
    """
    name = models.CharField(null=False,max_length=255)
    who_create = models.ForeignKey(User,models.CASCADE,null = False)
    published = models.BooleanField(default=False)
    for_everyone = models.BooleanField(default=True)
    rerunable = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"Name {self.name} everyone {self.for_everyone}"
    
    def save(self, *args, **kwargs):
        if self.pk:
            old = Survey.objects.get(pk = self.pk).for_everyone
            new = self.for_everyone
            if not old and new:
                SurveyUser.objects.filter(survey = self).delete()
        super().save(*args, **kwargs)
    

class SurveyQuesiton(models.Model): # Я поздно заметил это Quesiton...
    """
    Модель вопроса для опроса
    """
    question = models.CharField(null=False,max_length=255)
    survey_model = models.ForeignKey(Survey,models.CASCADE)
    
    class Meta:
        unique_together = [["question","survey_model"]]

class SurveyQuesitonOption(models.Model):
    """
    Модель варианта ответа для вопроса опроса
    """
    question = models.ForeignKey(SurveyQuesiton,models.CASCADE)
    option = models.CharField(null=False,max_length=255)

    class Meta:
        unique_together = [["question","option"]]   

class QuestionAnswerOption(models.Model):
    """
    Модель ответа для голосования
    """
    option = models.ForeignKey(SurveyQuesitonOption,models.CASCADE)
    user = models.ForeignKey(User,models.CASCADE)
    free_answer = models.CharField(null=True,max_length=255)
        
class SurveyUser(models.Model):
    """
    Модель m-t-m Пользователь <-> Опрос
    Показывает какой пользователь имеет доступ к опросу
    """
    user = models.ForeignKey(User,models.CASCADE)
    survey = models.ForeignKey(Survey,models.CASCADE)