from django.db import models
from authentication.models import User

class Vote(models.Model):
    """
    Модель голосования
    """
    name = models.CharField(null=False,max_length=255)
    who_create = models.ForeignKey(User,models.CASCADE,null = False)
    question = models.CharField(null=False,max_length=255)
    published = models.BooleanField(default=False)
    for_everyone = models.BooleanField(default=True)
    rerunable = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.name
    
class VoteOption(models.Model):
    """
    Модель варианта для голосования
    """
    choice = models.CharField(null=False,max_length=255)
    vote_model = models.ForeignKey(Vote,models.CASCADE)
    
    class Meta:
        unique_together = [["choice","vote_model"]]
        
class VoteAnswer(models.Model):
    """
    Модель ответа для голосования
    """
    option = models.ForeignKey(VoteOption,models.CASCADE)
    user = models.ForeignKey(User,models.CASCADE)
    
class VoteUser(models.Model):
    """
    Модель m-t-m Пользователь <-> Голосование
    Показывает какой пользователь имеет доступ к голосованию
    """
    user = models.ForeignKey(User,models.CASCADE)
    vote = models.ForeignKey(Vote,models.CASCADE)