from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = 'quiz'

router = DefaultRouter()
router.register('', views.QuizViewSet)


urlpatterns = [
    path('<int:quiz>/questions/', views.QuestionView.as_view(), name='questions'),
    path('start_quiz/', views.GameStarterView.as_view(), name='start_quiz'),
    path('finish_quiz/', views.GameEndView.as_view(), name='finish_quiz'),
    path('', include(router.urls)),
]
