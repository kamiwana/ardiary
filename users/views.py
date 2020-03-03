from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from .serializers import *
from django.contrib.auth.models import update_last_login
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi
class LoginAPI(generics.GenericAPIView):
    """
        로그인 API

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
        user.get_user_token(user)
        update_last_login(None, user)
        return Response(UserSerializer(user, context=self.get_serializer_context()).data)

class RegistrationAPI(generics.GenericAPIView):
    """
        회원가입 API

    ---
    # /auth/registration
    ## 내용
        - login_type : 0-ardiary, 1-네이버, 2-구글, 3-카카오, 4-페이스북, 5-인스타
    """
    
    serializer_class = CreateUserSerializer
    #user_response = openapi.Response('response description', UserSerializer)
    @swagger_auto_schema(responses={200:UserSerializer()})
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.get_user_token(user)
        return Response(UserSerializer(user, context=self.get_serializer_context()).data)


class UserAPI(generics.RetrieveAPIView):
    """
        회원정보 API

    ---
    #  /auth/user
    ## 내용
        - Header의 token값으로 회원정보 조회
        - login_type : 0-ardiary, 1-네이버, 2-구글, 3-카카오, 4-페이스북, 5-인스타
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    @swagger_auto_schema(responses={200: UserSerializer()})
    def get_object(self):
        return self.request.user

class ChangePasswordAPI(generics.GenericAPIView):
    """
        비밀번호변경 API

        ---
        # /auth/password_change
        ## 내용
            - Header의 token값으로 회원정보 조회
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer


    @swagger_auto_schema(responses={'200': '비밀번호가 변경되었습니다.'})
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response(
            {
                "result": 1,
                "message": '비밀번호가 변경되었습니다.'
            }
        )