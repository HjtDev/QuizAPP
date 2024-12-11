from rest_framework.serializers import ModelSerializer
from .models import Quiz, Question
from account.models import Player


class PlayerNameSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ('display_name',)

class QuizSerializer(ModelSerializer):
    author = PlayerNameSerializer(read_only=True)
    class Meta:
        model = Quiz
        fields = '__all__'


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
