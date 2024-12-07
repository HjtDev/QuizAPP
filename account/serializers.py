from rest_framework.serializers import Serializer, ModelSerializer, CharField, ValidationError
from .models import Player
from django.contrib.auth import authenticate


class PlayerSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'phone', 'name', 'display_name', 'score', 'league', 'created_at', 'updated_at')


class LoginSerializer(Serializer):
    phone = CharField(required=True)
    password = CharField(required=True, write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        user = authenticate(phone=phone, password=password)
        if not user:
            raise ValidationError('Invalid credentials')
        attrs['user'] = user
        return attrs
