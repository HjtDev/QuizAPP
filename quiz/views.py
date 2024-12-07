from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import Quiz, Question
from .serializers import QuizSerializer
from .permissions import IsOwnerOrAdmin


class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_permissions(self, *args, **kwargs):
        if self.action in ['list', 'create', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

