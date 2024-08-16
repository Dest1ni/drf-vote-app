from typing import Any
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
    rerunable = models.BooleanField(default=False) # todo Логика не реализована p.s. скорее всего и не нужна
    
    def __str__(self) -> str:
        return f"Name {self.name} everyone {self.for_everyone}"
    
    def save(self, *args, **kwargs): # Я заложник ИИ :(
        if self.pk:
            old = Vote.objects.get(pk = self.pk).for_everyone
            new = self.for_everyone
            if not old and new:
                VoteUser.objects.filter(vote = self).delete()
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = [['name','who_create']]
    

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

    class Meta:
        unique_together = [["option","user"]]
    
class VoteUser(models.Model):
    """
    Модель m-t-m Пользователь <-> Голосование
    Показывает какой пользователь имеет доступ к голосованию
    """
    user = models.ForeignKey(User,models.CASCADE)
    vote = models.ForeignKey(Vote,models.CASCADE)