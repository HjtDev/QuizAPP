from django.shortcuts import render
from .models import Player
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from .serializers import LoginSerializer, PlayerSerializer, RegisterSerializer


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            player = serializer.validated_data['user']
            player_data = PlayerSerializer(player).data
            return Response(player_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = Player.objects.all()
