from rest_framework import generics
from rest_framework.response import Response
from .serializers import *
from django.contrib.auth.models import update_last_login
from drf_yasg.utils import swagger_auto_schema
from users.utils import get_user
from utils import error_collection
from rest_framework import status
from ardiary.exception_handler import CustomValidation
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
    @swagger_auto_schema(
                         responses={
                             200: UserSerializer(),
                             400:
                                 error_collection.EMAIL_NOT_BLANK.as_md() +
                                 error_collection.USERNAME_NOT_BLANK.as_md() +
                                 error_collection.PASSWORD_INVALID.as_md() +
                                 error_collection.PASSWORD_INVALID_NOMAL.as_md() +
                                 error_collection.LOGIN_TYPE_NOT_BLANK.as_md() +
                                 error_collection.EMAIL_INVALID.as_md() +
                                 error_collection.USERNAME_INVALID.as_md() +
                                 error_collection.USERNAME_EXIST.as_md() +
                                 error_collection.NOT_FOUNT.as_md()
                            }
                         )
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data = {'result': 0, 'error': 'null', 'data': UserSerializer(user, context=self.get_serializer_context()).data}
            return Response(data)
        else:
            dict = serializer.errors

            if 'email' in dict:
                raise CustomValidation('-5', dict['email'][0])
            elif 'username' in dict:
                if 'blank' in dict['username'][0]:
                    raise CustomValidation('-2', "사용자 이름을 입력하세요.")
                elif '존재' in dict['username'][0]:
                    raise CustomValidation('-30', "해당 사용자 이름은 이미 존재합니다.")
                else:
                    raise CustomValidation('0', dict)
            elif 'password' in dict:
                if '8' in dict['password'][0]:
                    raise CustomValidation('-3', "비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.")
                else:
                    raise CustomValidation('0', dict)
            elif 'login_type' in dict:
                raise CustomValidation('-4', '로그인타입 ' + dict['login_type'][0])
            else:
                raise CustomValidation('0', dict)

class LoginAPI(generics.GenericAPIView):
    """
        로그인

        ---
        # /auth/login
    """
    serializer_class = LoginUserSerializer

    @swagger_auto_schema(
        responses={
             200: UserSerializer(),
             400:
                 error_collection.EMAIL_NOT_BLANK.as_md() +
                 error_collection.PASSWORD_INVALID.as_md() +
                 error_collection.EMAIL_INVALID.as_md() +
                 error_collection.EMAIL_PASSWORD_INVALID.as_md() +
                 error_collection.NOT_FOUNT.as_md()
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            update_last_login(None, user)
            data = {'result': 0, 'error': 'null',
                    'data': UserSerializer(user, context=self.get_serializer_context()).data}
            return Response(data)
        else:
            dict = serializer.errors
            if 'email' in dict:
                if 'blank' in dict['email'][0]:
                    raise CustomValidation('-1', "이메일 주소를 입력하세요.")
                else:
                    raise CustomValidation('-5', dict['email'][0])
            elif 'password' in dict:
                raise CustomValidation('-3', '비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.')
            else:
                raise CustomValidation('0', dict)

class UserAPI(generics.RetrieveAPIView):
    """
        회원정보

    ---
    #  /auth/user/{user}
    ## 내용
        - user :  로그인시 전달받은 사용자 id 값
    """
    serializer_class = UserSerializer

    @swagger_auto_schema(
        responses={
             200: UserSerializer(),
             400:
                 error_collection.USERNAME_NOT_FOUND.as_md()
        },
    )
    def get(self, request, user=None):
        user = get_user(user)
        serializer = self.serializer_class(user)
        data = {'result': 0, 'error': 'null', 'data': serializer.data}
        return Response(data)

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
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
               'error': openapi.Schema(type=openapi.TYPE_STRING, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호가 변경되었습니다.'),
                },
            ),
            400: error_collection.USER_INVALID.as_md()+
                 error_collection.CURRENT_PASSWORD_NOT_BLANK.as_md() +
                 error_collection.CURRENT_PASSWORD_INVALID.as_md() +
                 error_collection.CHANGE_PASSWORD_NOT_BLANK.as_md() +
                 error_collection.CHANGE_PASSWORD_INVALID.as_md() +
                 error_collection.NOT_FOUNT.as_md()
        },
    )
    def post(self, request, *args, **kwargs):

        user = request.data.get("user")

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            dict = serializer.errors
            if 'user' in dict:
                if 'integer' in dict['user'][0]:
                    raise CustomValidation('-9', "user에 "+dict['user'][0])
                else:
                    raise CustomValidation('0', dict['user'][0])
            elif 'current_password' in dict:
                if 'blank' in dict['current_password'][0]:
                    raise CustomValidation('-10', "기존 비밀번호를 입력하세요.")
                else:
                    raise CustomValidation('0', dict['current_password'][0])
            elif 'new_password' in dict:
                if 'blank' in dict['new_password'][0]:
                    raise CustomValidation('-12', "변경할 비밀번호를 입력하세요.")
                else:
                    raise CustomValidation('-13', "변경할 "+dict['new_password'][0])
            else:
                raise CustomValidation('0', dict)

        user = get_user(user)
        if not user.check_password(serializer.validated_data['current_password']):
            raise CustomValidation('-11', '기존 비밀번호가 다릅니다.')

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {
                "result": 1,
                "error": 'null',
                "data": '비밀번호가 변경되었습니다.'
            }
        )