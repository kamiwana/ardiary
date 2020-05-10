from .serializers import *
from ardiary.exception_handler import CustomValidation

def create_user_account(email, username,  password,
                        login_type, **extra_fields):

    user = get_user_model().objects.create_user(
        email=email, password=password, username=username, login_type=login_type,
        **extra_fields)

    return user

def get_user(pk):
    if pk is not None:
        if len(pk) < 1 or pk.isdigit() is False:
            raise CustomValidation('-8', "존재하지 않는 ID 입니다.")
        try:
            user = get_user_model().objects.get(id=pk)
            return user
        except get_user_model().DoesNotExist:
            raise CustomValidation('-8', "존재하지 않는 ID 입니다.")
    else:
        raise CustomValidation('-8', "존재하지 않는 ID 입니다.")