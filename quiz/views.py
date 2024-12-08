from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Quiz, Question
from .serializers import QuizSerializer, QuestionSerializer
from .permissions import IsOwnerOrAdmin, IsQuizOwnerOrAdmin
from rest_framework.views import APIView


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


class QuestionView(APIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsQuizOwnerOrAdmin]

    def get(self, request, *args, **kwargs):
        quiz_id = kwargs.get('quiz')
        try:
            questions = Quiz.objects.get(pk=quiz_id).questions.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        quiz_id = kwargs.get('quiz')
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            serializer = QuestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(quiz=quiz)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        quiz_id = kwargs.get('quiz')
        question_id = request.data.get('id')
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            question = quiz.questions.get(pk=question_id)
            serializer = QuestionSerializer(question, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        except Question.DoesNotExist:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        quiz_id = kwargs.get('quiz')
        question_id = request.data.get('id')
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            question = quiz.questions.get(pk=question_id)
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        except Question.DoesNotExist:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
