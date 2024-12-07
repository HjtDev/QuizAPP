from django.db import models
from account.models import Player


class Quiz(models.Model):
    author = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='quizzes', verbose_name='Author')
    title = models.CharField(max_length=200, verbose_name='Quiz Title')
    description = models.TextField(verbose_name='Quiz Description')
    available_time = models.DurationField(verbose_name='Available Time')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return self.title
