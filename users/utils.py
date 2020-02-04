from django.contrib.auth import get_user_model

def create_user_account(email, password, customuser_name="",
                        login_type="", **extra_fields):
    user = get_user_model().objects.create_user(
        email=email, password=password, username=email, customuser_name=customuser_name, login_type = login_type,
        **extra_fields)

    return user