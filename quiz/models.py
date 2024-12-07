from django.db import models
from account.models import Player


class Quiz(models.Model):
    author = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='quizzes', verbose_name='Author')
    title = models.CharField(max_length=200, verbose_name='Quiz Title')
    description = models.TextField(verbose_name='Quiz Description')
    available_time = models.DurationField(verbose_name='Available Time')

    verified = models.BooleanField(default=False, verbose_name='Verified')
    score = models.PositiveIntegerField(default=0, verbose_name='Score (XP)')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='Quiz')

    question = models.TextField(verbose_name='Question')

    option_a = models.CharField(max_length=255, verbose_name='Option A')
    option_b = models.CharField(max_length=255, verbose_name='Option B')
    option_c = models.CharField(max_length=255, verbose_name='Option C')
    option_d = models.CharField(max_length=255, verbose_name='Option D')

    class CorrectAnswers(models.TextChoices):
        option_a = ('a', 'A')
        option_b = ('b', 'B')
        option_c = ('c', 'C')
        option_d = ('d', 'D')

    correct_answer = models.CharField(max_length=1, choices=CorrectAnswers.choices, verbose_name='Correct Answer')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return self.question

