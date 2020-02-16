from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation, authenticate
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import BaseUserManager
from rest_framework.authtoken.models import Token
from .utils import create_user_account

class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다")

class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField('get_user_token')

    def get_user_token(self, obj):
        token = Token.objects.get(user=obj)
        return token.key

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "username", "login_type", "token")

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


    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('기존 비밀번호가 다릅니다.')
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

class AuthUserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'username', 'login_type', )

    def get_auth_token(self, obj):
        token = Token.objects.create(user=obj)
        return token.key