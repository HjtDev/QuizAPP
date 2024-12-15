from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication

from .models import Player
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from .serializers import LoginSerializer, PlayerSerializer, RegisterSerializer
from .permissions import IsAccountOwnerOrAdmin


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


class PlayerRetrieveView(RetrieveAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAccountOwnerOrAdmin]
    authentication_classes = [BasicAuthentication]


class PlayerUpdateView(UpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAccountOwnerOrAdmin]
    authentication_classes = [BasicAuthentication]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.validated_data.pop('password', None)
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

