from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Quiz, Question
from .serializers import QuizSerializer, QuestionSerializer
from .permissions import IsOwnerOrAdmin, IsQuizOwnerOrAdmin
from rest_framework.views import APIView
from datetime import datetime as dt
from django.core.cache import cache
from account.models import Player


class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.filter(verified=True)
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


class GameStarterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        player_id = request.data.get('player_id')
        quiz_id = request.data.get('quiz_id')

        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            if not quiz.verified:
                raise PermissionDenied("Quiz is not verified.")

            cache.set(f'player_{player_id}:{quiz_id}', quiz.score, timeout=int(quiz.available_time.total_seconds()))

        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_200_OK)


class GameEndView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        player_id = request.data.get('player_id')
        quiz_id = request.data.get('quiz_id')
        answers = request.data.get('answers')

        try:
            score = cache.get(f'player_{player_id}:{quiz_id}')
            if score is None:
                return Response({'error': 'You did not finish the quiz before timeout.'},
                                status=status.HTTP_400_BAD_REQUEST)

            quiz = Quiz.objects.get(pk=quiz_id)
            questions = quiz.questions.all()
            number_of_questions = questions.count()

            reward = self.calculate_reward(answers, questions, score, number_of_questions)

            player = Player.objects.get(pk=player_id)
            player.score += int(reward)
            player.save()

            cache.delete(f'player_{player_id}:{quiz_id}')

            return Response({'score': reward}, status=status.HTTP_200_OK)

        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Player.DoesNotExist:
            return Response({'error': 'Player not found.'}, status=status.HTTP_404_NOT_FOUND)

    def calculate_reward(self, answers, questions, score, number_of_questions):
        reward = 0
        for question_id, answer in answers.items():
            try:
                correct_answer = questions.get(pk=question_id).correct_answer
                if answer == correct_answer:
                    reward += score / number_of_questions
            except Question.DoesNotExist:
                continue
        return reward
