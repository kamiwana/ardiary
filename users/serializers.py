from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation, authenticate
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import BaseUserManager
from .utils import create_user_account

class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user

        data = {'login': '이메일 또는 비밀번호가 올바르지 않습니다.'}
        raise serializers.ValidationError(data)

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "username", "login_type")

class CreateUserSerializer(serializers.ModelSerializer):
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
        user = get_user_model().objects.filter(email=value)
        if user:
            raise serializers.ValidationError("이미 등록된 이메일주소입니다.")
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        try:
            validators.validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    user = serializers.IntegerField(required=True, help_text="foo bar")

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value
