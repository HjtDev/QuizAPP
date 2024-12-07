from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class PlayerManager(BaseUserManager):
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
        extra_fields.setdefault('is_active', True)
        return self.create_user(phone, password, **extra_fields)

class Player(AbstractBaseUser, PermissionsMixin):
    class League(models.TextChoices):
        NO_LEAGUE = 'no_league', 'No League'
        BRONZE = 'bronze', 'Bronze'
        SILVER = 'silver', 'Silver'
        GOLD = 'gold', 'Gold'
        MASTER = 'master', 'Master'

    phone = models.CharField(max_length=11, unique=True, verbose_name='Phone Number')
    name = models.CharField(max_length=50, verbose_name='Full Name')
    display_name = models.CharField(max_length=50, verbose_name='Display Name')

    is_active = models.BooleanField(default=True, verbose_name='Active Status')
    is_staff = models.BooleanField(default=False, verbose_name='Staff Status')
    is_superuser = models.BooleanField(default=False, verbose_name='Superuser Status')

    score = models.IntegerField(default=0, verbose_name='Score')
    league = models.CharField(max_length=10, choices=League.choices, default=League.NO_LEAGUE, verbose_name='League')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name', 'display_name']

    objects = PlayerManager()

    def save(self, *args, **kwargs):
        if self.score < 1000:
            self.league = self.League.NO_LEAGUE
        elif 1000 <= self.score < 2000:
            self.league = self.League.BRONZE
        elif 2000 <= self.score < 3500:
            self.league = self.League.SILVER
        elif 3500 <= self.score < 6000:
            self.league = self.League.GOLD
        else:
            self.league = self.League.MASTER
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name
