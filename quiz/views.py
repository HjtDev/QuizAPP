from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .models import Quiz, Question
from .serializers import QuizSerializer, QuestionSerializer
from .permissions import IsOwnerOrAdmin, IsQuizOwnerOrAdmin
from rest_framework.views import APIView
from django.core.cache import cache
from account.models import Player


class QuizViewSet(ModelViewSet):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.filter(verified=True)

    @action(detail=True, methods=['get'], url_name='get_my_quizzes', url_path='my_quizzes')
    def my_quizzes(self, request, pk=None):
        quizzes = Quiz.objects.filter(author_id=pk)
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        if self.action == 'retrieve' or self.action == 'destroy':
            return Quiz.objects.all()
        return self.queryset


    def get_permissions(self, *args, **kwargs):
        if self.action in ['list', 'create', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.verified = False
        instance.save()


class QuestionView(APIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsQuizOwnerOrAdmin]

    def get(self, request, *args, **kwargs):
        quiz_id = kwargs.get('quiz')
        try:
            if 'id' in request.data:
                question = Question.objects.get(id=request.data['id'])
                serializer = QuestionSerializer(question)
            else:
                questions = Quiz.objects.get(pk=quiz_id).questions.all()
                serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        quiz_id = kwargs.get('quiz')
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            request.data.update({'quiz': quiz_id})
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
                quiz.verified = False
                quiz.save()
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

            if f'player_{player_id}:{quiz_id}' in cache.keys('*'):
                raise PermissionDenied("Quiz already started.")

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
            player.score += reward
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
                if answer == questions.get(pk=int(question_id)).correct_answer:
                    reward += score / number_of_questions
            except Question.DoesNotExist:
                continue
        return int(reward)
