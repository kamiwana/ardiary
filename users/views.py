from rest_framework import  generics
from rest_framework.response import Response
from .serializers import *
from django.contrib.auth.models import update_last_login
from drf_yasg.utils import swagger_auto_schema
from users.utils import get_user
from rest_framework import status
from rest_framework.decorators import api_view

from drf_yasg import openapi

user = openapi.Parameter('user', in_=openapi.IN_QUERY, description='로그인시 전달받은 사용자 id 값',
                                type=openapi.TYPE_INTEGER)

class RegistrationAPI(generics.GenericAPIView):
    """
        회원가입

    ---
    # /auth/registration
    ## 내용
        - login_type : 0- ardiary, 1-네이버, 2-구글, 3-카카오, 4-페이스북, 5-인스타
    """
    
    serializer_class = CreateUserSerializer
    @swagger_auto_schema(responses={200:UserSerializer()})
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user, context=self.get_serializer_context()).data)

class LoginAPI(generics.GenericAPIView):
    """
        로그인

        ---
        # /auth/login
        ## 내용
            - login_type : 0-ardiary, 1-네이버, 2-구글, 3-카카오, 4-페이스북, 5-인스타
    """
    serializer_class = LoginUserSerializer

    @swagger_auto_schema(responses={200: UserSerializer()})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        update_last_login(None, user)
        return Response(UserSerializer(user, context=self.get_serializer_context()).data)

class UserAPI(generics.RetrieveAPIView):
    """
        회원정보

    ---
    #  /auth/user/{user}
    ## 내용
        - user :  로그인시 전달받은 사용자 id 값
        - login_type : 0-ardiary, 1-네이버, 2-구글, 3-카카오, 4-페이스북, 5-인스타
    """
    serializer_class = UserSerializer

    @swagger_auto_schema(responses={200: UserSerializer()})
    def get(self, request, user=None):
        user = get_user(user)
        serializer = self.serializer_class(user)
        return Response(serializer.data)

class ChangePasswordAPI(generics.GenericAPIView):
    """
        비밀번호변경 API

    ---
    # /auth/password_change
    """
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(request_body=openapi.Schema(

        type=openapi.TYPE_OBJECT,
        required=['user', 'current_password', 'new_password'],
        properties={
            'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인시 전달받은 사용자 id 값'),
            'current_password': openapi.Schema(type=openapi.TYPE_STRING, description='현재 비밀번호'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='변경될 비밀번호')
        },
    ),
        responses={
            status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
               'field': openapi.Schema(type=openapi.TYPE_INTEGER, description='change_password'),
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호가 변경되었습니다.'),
                },
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0'),
                    'field': openapi.Schema(type=openapi.TYPE_INTEGER, description='current_password'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='기존 비밀번호가 다릅니다.'),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        user = request.data.get("user")
        user = get_user(user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data['current_password']):
            data = {"current_password": '기존 비밀번호가 다릅니다.'}
            raise serializers.ValidationError(data)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {
                "result": 1,
                "field": 'change_password',
                "message": '비밀번호가 변경되었습니다.'
            }
        )