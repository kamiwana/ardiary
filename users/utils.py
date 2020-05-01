from django.contrib.auth import get_user_model
from .serializers import *

def create_user_account(email, username,  password,
                        login_type="", **extra_fields):
    user = get_user_model().objects.create_user(
        email=email, password=password, username=username, login_type = login_type,
        **extra_fields)

    return user

def get_user(pk):
    try:
        user = get_user_model().objects.get(id=pk)
        return user
    except get_user_model().DoesNotExist:
        data = {"user": '존재하지 않는 ID 입니다.'}
        raise serializers.ValidationError(data)