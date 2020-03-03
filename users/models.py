from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.authtoken.models import Token
from .choices import *

class CustomUser(AbstractUser):
    login_type = models.SmallIntegerField(choices=LOGIN_TYPE, default=0, null=False,  verbose_name='로그인 타입')

    def get_user_token(self, user):
        return Token.objects.get_or_create(user=user)

    def create_user(self, email, username, login_type, password=None):
        if not email:
            raise ValueError('유효한 이메일 주소를 입력하십시오.')
        elif not username:
            raise ValueError('이름을 입력하십시오.')
        elif not login_type:
            raise ValueError('로그인타입을 입력하십시오.')
        user = self.model(
            username=username,
            login_type=login_type,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user