from django.contrib.auth.models import AbstractUser
from django.db import models
from .choices import *
from rest_framework import serializers

class CustomUser(AbstractUser):
    login_type = models.SmallIntegerField(choices=LOGIN_TYPE, default=0, null=False, blank=False, verbose_name='로그인 타입')

    def create_user(self, email, username, login_type, password=None):

        user = self.model(
            username=username,
            login_type=login_type,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
