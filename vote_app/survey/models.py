from django.db import models
from authentication.models import User

#class Survey(models.Model):
#    """
#    Модель опроса
#    """
#    name = models.CharField(null=False,max_length=255)
#    who_create = models.ForeignKey(User,models.CASCADE,null = False)
#    published = models.BooleanField(default=False)
#    for_everyone = models.BooleanField(default=True)
#    rerunable = models.BooleanField(default=False)
#    
#    def __str__(self) -> str:
#        return f"Name {self.name} everyone {self.for_everyone}"
#    
#    #def save(self, *args, **kwargs): # Я заложник ИИ :(
#    #    if self.pk:
#    #        old = Vote.objects.get(pk = self.pk).for_everyone
#    #        new = self.for_everyone
#    #        if not old and new:
#    #            VoteUser.objects.filter(vote = self).delete()
#    #    super().save(*args, **kwargs)
#
#class SurveyQuesiton(models.Model):
#    """
#    Модель варианта для голосования
#    """
#    question = models.CharField(null=False,max_length=255)
#    survey_model = models.ForeignKey(Survey,models.CASCADE)
#    
#    class Meta:
#        unique_together = [["question","survey_model"]]
#
#class SurveyQuesitonOption(models.Model):
#    question = models.ForeignKey(SurveyQuesiton,models.CASCADE)
#    
#
#class VoteAnswer(models.Model):
#    """
#    Модель ответа для голосования
#    """
#    option = models.ForeignKey(VoteOption,models.CASCADE)
#    user = models.ForeignKey(User,models.CASCADE)
#    
#class VoteUser(models.Model):
#    """
#    Модель m-t-m Пользователь <-> Голосование
#    Показывает какой пользователь имеет доступ к голосованию
#    """
#    user = models.ForeignKey(User,models.CASCADE)
#    vote = models.ForeignKey(Vote,models.CASCADE)