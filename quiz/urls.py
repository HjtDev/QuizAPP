from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = 'quiz'

router = DefaultRouter()
router.register('', views.QuizViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('<int:quiz>/questions/', views.QuestionView.as_view(), name='questions'),
]
