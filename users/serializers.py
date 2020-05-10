from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation, authenticate
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import BaseUserManager
from .utils import create_user_account
from ardiary.exception_handler import CustomValidation
from rest_framework import status

class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise CustomValidation('-7', "이메일 또는 비밀번호가 올바르지 않습니다.")

class UserSerializer(serializers.ModelSerializer):
    login_type = serializers.IntegerField(required=True,
                                            help_text="0-ardiary, 1-네이버, 2-구글, 3-카카오, 4-페이스북, 5-인스타")

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "username", "login_type")

class CreateUserSerializer(serializers.ModelSerializer):
    login_type = serializers.CharField(required=True)
    class Meta:
        model = get_user_model()
        fields = ("email", "username", "password", "login_type")
        extra_kwargs = {"password": {"write_only": True, 'min_length': 8}}

    def create(self, validated_data):

        user = create_user_account(validated_data['email'], validated_data['username'], validated_data['password'],
                                  validated_data['login_type'])
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_email(self, value):
        if not value:
            raise CustomValidation('-1', "이메일주소를 입력하세요.")
        user = get_user_model().objects.filter(email=value)
        if user:
            raise CustomValidation('-5', "이미 등록된 이메일주소입니다.")
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        try:
            validators.validate_password(value)
        except ValidationError as exc:
            if '일상적인' in str(exc):
                raise CustomValidation('-29', "비밀번호가 너무 일상적인 단어입니다.")
            else:
                raise CustomValidation('-7', str(exc))
        return value

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    user = serializers.IntegerField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value