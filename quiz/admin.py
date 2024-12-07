from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    verbose_name = 'Question'
    verbose_name_plural = 'Questions'


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'verified', 'score', 'created_at', 'updated_at')
    list_filter = ('author', 'verified', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    inlines = [QuestionInline]
