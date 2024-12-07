from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)

class Player(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=11, unique=True, verbose_name='Phone Number')
    name = models.CharField(max_length=50, verbose_name='Full Name')
    display_name = models.CharField(max_length=50, verbose_name='Display Name')

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name', 'display_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.phone
