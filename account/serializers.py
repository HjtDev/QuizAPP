from rest_framework.serializers import Serializer, ModelSerializer, CharField, ValidationError
from .models import Player
from django.contrib.auth import authenticate, password_validation


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


class RegisterSerializer(Serializer):
    phone = CharField(required=True)
    name = CharField(required=True)
    display_name = CharField(required=True)
    password = CharField(required=True, write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        name: str = attrs.get('name')
        display_name = attrs.get('display_name')
        password = attrs.get('password')

        if not (phone and phone.startswith('09') and len(phone) == 11 and phone.isdigit()):
            raise ValidationError('Invalid phone number')

        if Player.objects.filter(phone=phone).exists():
            raise ValidationError('Phone number already in use')

        if not (name and name.isascii()):
            raise ValidationError('Invalid name')

        if not display_name or len(display_name) < 3:
            raise ValidationError('Invalid display_name')

        password_validation.validate_password(password)

        return attrs

    def create(self, validated_data):
        player = Player(phone=validated_data['phone'], name=validated_data['name'],
                        display_name=validated_data['display_name'])
        player.set_password(validated_data['password'])
        player.save()
        return player
