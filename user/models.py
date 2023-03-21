from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):

    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))
        if not phone_number:
            raise ValueError(_('Users must have a phone number'))

        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, phone_number, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone_regex = RegexValidator(regex='^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$',)
    phone_number = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    first_name = models.CharField(verbose_name='First Name', max_length=250)
    last_name = models.CharField(verbose_name='Last Name', max_length=250)
    password = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    money = models.DecimalField(default=0, decimal_places=2, max_digits=19)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('phone_number',)

    objects = CustomUserManager()

    def __str__(self):
        return self.email







