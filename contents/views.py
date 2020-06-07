from rest_framework.generics import CreateAPIView
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from users.utils import get_user
from ardiary.exception_handler import CustomValidation
from utils import error_collection
from .utils import *

user = openapi.Parameter('user', in_=openapi.IN_QUERY, description='로그인시 전달받은 사용자 id 값',
                                type=openapi.TYPE_INTEGER)
contents = openapi.Parameter('contents', in_=openapi.IN_QUERY, description='contents id ',
                                type=openapi.TYPE_INTEGER)
parent_id = openapi.Parameter('parent_id', in_=openapi.IN_QUERY, description='parent_id',
                                type=openapi.TYPE_INTEGER)
activation_code = openapi.Parameter('activation_code', in_=openapi.IN_QUERY,
                                    description='시리얼번호, 컨텐츠 등록시에만 보냄, 컨텐츠 조회시에는 보내지 않음',
                                type=openapi.TYPE_INTEGER)

class ContentsFilesCreateAPI(APIView):

    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ContentsCreateFilesSerializer
    queryset = ContentsFiles.objects.all()
    serializer = serializer_class(queryset, many=True)

    def post(self, request, *args, **kwargs):

        user = get_user(request.data['user'])

        contentsfiles_serializer = self.serializer_class(data=request.data)
        if contentsfiles_serializer.is_valid():
            contentsfiles_serializer.save()
            return Response(contentsfiles_serializer.data, status=status.HTTP_201_CREATED)
        else:
            data = {"contents_files": contentsfiles_serializer.errors}
            raise serializers.ValidationError(data)

class ContentsCreateAPI(APIView):

    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ContentsSerializer
    queryset = Contents.objects.all()
    serializer = serializer_class(queryset, many=True)

    @swagger_auto_schema(request_body=ContentsCreateRequestSerializer,
         responses={
             200: QRDatasSerializer,
             400:
                 error_collection.ACTIVATION_CODE_INVALID.as_md() +
                 error_collection.QRDATA_HAS_CONTENTS.as_md() +
                 error_collection.QRDATA_NOT_FOUNDS.as_md() +
                 error_collection.NOT_FOUNT.as_md()
             },
         )
    def post(self, request, *args, **kwargs):
        """
           컨텐츠 작성

            ---
            # /contents/

        """

        get_user(request.data['user'])
        qr_data = request.data['qr_data']
        activation_code = request.data['activation_code']

        try:
            qrdats = QRDatas.objects.get(qr_data=qr_data)

            if activation_code:
                if str(qrdats.activation_code) != activation_code:
                    raise CustomValidation('-14', "등록된 시리얼 번호가 없습니다.")
            else:
                raise CustomValidation('-14', "등록된 시리얼 번호가 없습니다.")

            if qrdats.is_active == 1:
                raise CustomValidation('-15', "컨텐츠가 등록된 QR코드 입니다.")

        except QRDatas.DoesNotExist:
             raise CustomValidation('-16', "등록된 QR코드가 없습니다.")

        try:
            Contents.objects.get(qr_data__qr_data=qr_data)
            raise CustomValidation('-15', "컨텐츠가 등록된 QR코드 입니다.")

        except Contents.DoesNotExist:
            contents_serializer = ContentsSerializer(data=request.data)
            if contents_serializer.is_valid():
                contents_serializer.save()
                data = {'result': 0, 'error': 'null', 'data': contents_serializer.data}
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                raise CustomValidation('0', contents_serializer.errors)


class ContentsUpdateAPI(APIView):
    """
       컨텐츠 수정

        ---
        # /contents/{id}/{user}
        ## 내용
            - user :  로그인시 전달받은 사용자 id 값
    """
    parser_classes = (MultiPartParser,)
    serializer_class = ContentsUpdateSerializer
    queryset = Contents.objects.all()
    serializer = serializer_class(queryset, many=True)

    @swagger_auto_schema(
         request_body=ContentsUpdateRequestSerializer,
         responses={
             200: ContentsUpdateSerializer,
             400:
                 error_collection.CONTENTS_NOT_FOUNDS.as_md() +
                 error_collection.CONTENTS_CHECK_USER.as_md() +
                 error_collection.NOT_FOUNT.as_md()
            },
         )
    def post(self, request, pk=None, user=None):

        user = get_user(user)
        contents = get_contents(pk)

        if user.pk != contents.user.pk:
            raise CustomValidation('-18', '작성자만 수정 가능합니다.')

        serializer = ContentsUpdateSerializer(contents, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            data = {'result': 0, 'error': 'null', 'data': serializer.data}
            return Response(data, status=status.HTTP_200_OK)
        else:
            raise CustomValidation('0', serializer.errors)

class QRDataDetailAPI(APIView):
    serializer_class = QRDatasSerializer
    queryset = QRDatas.objects.all()

    @swagger_auto_schema(manual_parameters=[activation_code],
        responses={
            200: QRDatasSerializer,
            400:
                error_collection.QRDATA_NOT_FOUNDS.as_md() +
                error_collection.ACTIVATION_CODE_INVALID.as_md() +
                error_collection.CONTENTS_DETAIL_NOT_FOUNDS.as_md() +
                error_collection.NOT_FOUNT.as_md()
        },
    )
    def get(self, request, qr_data=None):
        """
            QR코드, 시리얼번호 체크 , 컨텐츠 가져오기

            ---
            # /contents/qrdatas/{qr_data}?activation_code={activation_code}
            ## 내용
                - recog_type : 1-이미지기반, 2-공간기반, 3-음성기반
                - link_01_type, link_02_type : 1-페이스북, 2-사진, 3-쇼핑몰, 4-전화번호, 5-카카오톡, 6-카카오톡, 7-유튜브, 8-기타URL
                - effect_type : 1-폭죽, 2-스노우, 3-선물상자
                - char_type : 1-사람, 2-팬더
                - contents_comment : 댓글 리스트
                - contents_files : 등록된 파일리스트
        """

        try:
            qr_data = QRDatas.objects.get(qr_data=qr_data)
        except QRDatas.DoesNotExist:
            raise CustomValidation('-16', '등록된 QR코드가 없습니다.')

        activation_code = self.request.GET.get("activation_code")
        if activation_code:
            if str(qr_data.activation_code) != activation_code:
                raise CustomValidation('-14', '등록된 시리얼 번호가 없습니다.')
        try:
            contents = Contents.objects.get(pk=qr_data.qrdatascontents.pk)
            contents.view_count = contents.view_count + 1
            contents.save()

            serializer = self.serializer_class(qr_data)
            data = {'result': 0, 'error': 'null', 'data': serializer.data}
            return Response(data)
        except:

          res_data = {
              "qr_data": qr_data.qr_data,
              "activation_code": qr_data.activation_code,
              "contents_type": qr_data.contents_type
          }

          data = {
                "result": 19,
                "error": "등록된 컨텐츠가 없습니다.",
                "data": res_data
            }
          return Response(data, status=status.HTTP_200_OK)

class ContentsDetailAPI(APIView):
    serializer_class = QRDatasSerializer
    queryset = QRDatas.objects.all()

    @swagger_auto_schema(
        responses={
            200: QRDatasSerializer,
            400:
                error_collection.QRDATA_NOT_FOUNDS.as_md() +
                error_collection.CONTENTS_NOT_FOUNDS.as_md() +
                error_collection.NOT_FOUNT.as_md()
        },
    )
    def get(self, request, qr_data=None):
        """
              QRCode로 컨텐츠 조회

            ---
            # /contents/{qr_data}
            ## 내용
                - recog_type : 1-이미지기반, 2-공간기반, 3-음성기반
                - link_01_type, link_02_type : 1-페이스북, 2-사진, 3-쇼핑몰, 4-전화번호, 5-카카오톡, 6-카카오톡, 7-유튜브, 8-기타URL
                - effect_type : 1-폭죽, 2-스노우, 3-선물상자
                - char_type : 1-사람, 2-팬더
                - contents_comment : 댓글 리스트
                - contents_files : 등록된 파일리스트
        """

        try:
            qr_data = QRDatas.objects.get(qr_data=qr_data)
        except QRDatas.DoesNotExist:
            raise CustomValidation('-16', '등록된 QR코드가 없습니다.')

        try:
            contents = Contents.objects.get(pk=qr_data.qrdatascontents.pk)

            serializer = self.serializer_class(qr_data)
            data = {'result': 0, 'error': 'null', 'data': serializer.data}
            return Response(data)
        except Contents.DoesNotExist:
            data = {
                "result": 19,
                "error": "등록된 컨텐츠가 없습니다.",
                "data": "{}"
            }
            return Response(data, status=status.HTTP_200_OK)
class ContentsListAPI(APIView):
    serializer_class = ContentsSerializer
    queryset = Contents.objects.all()

    @swagger_auto_schema(
        responses={
            200: ContentsSerializer,
            400:
                error_collection.CONTENTS_NOT_FOUNDS.as_md() +
                error_collection.NOT_FOUNT.as_md()
        },
    )
    def get(self, request, user=None):
        """
              로그인 유저의 보유 AR List API

            ---
            # /contents/list/{user}
            ## 내용
                - recog_type : 1-이미지기반, 2-공간기반, 3-음성기반
                - link_01_type, link_02_type : 1-페이스북, 2-사진, 3-쇼핑몰, 4-전화번호, 5-카카오톡, 6-카카오톡, 7-유튜브, 8-기타URL
                - effect_type : 1-폭죽, 2-스노우, 3-선물상자
                - char_type : 1-사람, 2-팬더
                - contents_comment : 댓글 리스트
                - contents_files : 등록된 파일리스트
        """

        try:
            contents = Contents.objects.filter(user=user)

            serializer = self.serializer_class(contents, many=True)
            data = {'result': 0, 'error': 'null', 'data': serializer.data}
            return Response(data)
        except Contents.DoesNotExist:
            data = {
                "result": 19,
                "error": "등록된 컨텐츠가 없습니다.",
                "data": "{}"
            }
            return Response(data, status=status.HTTP_200_OK)

class ContentsPasswordCreateAPI(APIView):
    """
    컨텐츠 비밀번호  설정

    ---
    # /contents/password/create
    """

    serializer_class = ContentsPasswordSerializer
    queryset = ContentsPassword.objects.all()
    serializer = serializer_class(queryset)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user', 'contents', 'password'],
        properties={
            'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인시 전달받은 사용자 id 값'),
            'contents': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents id'),
            'password': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents password')
        },
    ),
        responses={
            status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
               'error': openapi.Schema(type=openapi.TYPE_STRING, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호가 설정되었습니다.'),
                },
            ),
            400:
                error_collection.CONTENTS_PASSWORD_NOT_BLANK.as_md() +
                error_collection.CONTENTS_PASSWORD_INVALID.as_md() +
                error_collection.CONTENTS_PASSWORD_DIGIT.as_md() +
                error_collection.CONTENTS_HAS_PASSWORD.as_md() +
                error_collection.NOT_FOUNT.as_md()
        },
    )
    def post(self, request, *args, **kwargs):

        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_contents(contents_pk)

        if user != contents.user:
            raise CustomValidation('-20', '컨텐츠를 등록한 사용자가 아닙니다.')

        serializer = ContentsPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {'result': 1, 'error': 'null', 'data': '비밀번호가 설정되었습니다.'}
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            dict = serializer.errors
            if 'contents' in dict and 'unique' in dict['contents'][0]:
                raise CustomValidation('-24', '비밀번호가 이미 설정되었습니다.')
            elif 'password' in dict:
                if 'blank' in dict['password'][0]:
                    raise CustomValidation('-21', '비밀번호를 입력하세요.')
                elif '4' in dict['password'][0]:
                    raise CustomValidation('-22', '비밀번호는 4자리입니다.')
            raise CustomValidation('0', dict)

class ContentsPasswordUpdateAPI(APIView):
    """
    컨텐츠 비밀번호 수정

    ---
    # /contents/password/update
    """

    serializer_class = ContentsPasswordSerializer
    queryset = ContentsPassword.objects.all()
    serializer = serializer_class(queryset)

    @swagger_auto_schema(request_body=openapi.Schema(

        type=openapi.TYPE_OBJECT,
        required=['user', 'contents', 'password'],
        properties={
            'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인시 전달받은 사용자 id 값'),
            'contents': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents id'),
            'password': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents password')
        },
    ),
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
               'error': openapi.Schema(type=openapi.TYPE_INTEGER, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호가 수정되었습니다.'),
                },
            ),
            400:
                error_collection.CONTENTS_NOT_FOUNDS.as_md() +
                error_collection.CONTENTS_HAS_NOT_USER.as_md() +
                error_collection.CONTENTS_PASSWORD_NOT_BLANK.as_md() +
                error_collection.CONTENTS_PASSWORD_INVALID.as_md() +
                error_collection.CONTENTS_PASSWORD_DIGIT.as_md() +
                error_collection.CONTENTS_PASSWORD_NOT_FOUND.as_md() +
                error_collection.NOT_FOUNT.as_md()
        },
    )
    def post(self, request, *args, **kwargs):
        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_contents(contents_pk)

        if user != contents.user:
            raise CustomValidation('-20', '컨텐츠를 등록한 사용자가 아닙니다.')

        try:
            queryset = ContentsPassword.objects.get(contents=contents)
        except ContentsPassword.DoesNotExist:
            raise CustomValidation('-25', '등록된 비밀번호가 없습니다.')
        
        serializer = ContentsPasswordSerializer(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {'result': 1, 'error': 'null', 'data': '비밀번호가 수정되었습니다.'}
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            dict = serializer.errors
            if 'password' in dict:
                if 'blank' in dict['password'][0]:
                    raise CustomValidation('-21', '비밀번호를 입력하세요.')
                elif '4' in dict['password'][0]:
                    raise CustomValidation('-22', "비밀번호는 4자리입니다.")
            raise CustomValidation('0', dict)

class ContentsPasswordAPI(APIView):
    """
    컨텐츠 비밀번호 확인

    ---
    # /contents/password
    """

    serializer_class = ContentsPasswordSerializer
    queryset = ContentsPassword.objects.all()
    serializer = serializer_class(queryset)

    @swagger_auto_schema(request_body=openapi.Schema(

        type=openapi.TYPE_OBJECT,
        required=['user', 'contents', 'password'],
        properties={
            'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인시 전달받은 사용자 id 값'),
            'contents': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents id'),
            'password': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents password')
        },
    ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                   'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
                   'error': openapi.Schema(type=openapi.TYPE_INTEGER, description='null'),
                   'data': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호가 일치합니다.'),
                    },
            ),
            400:
                error_collection.CONTENTS_NOT_FOUNDS.as_md() +
                error_collection.CONTENTS_PASSWORD_NOT_MATCH.as_md()
        },
    )
    def post(self, request, *args, **kwargs):

        #로그인 체크
        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        # 컨텐츠 여부 체크
        contents_pk = self.request.data.get('contents', None)
        contents = get_contents(contents_pk)

        # 패스워드 체크
        contents_password = self.request.data.get('password', None)

        if contents_password == contents.contentspassword.password:
            data = {'result': 1, 'error': 'null', 'data': '비밀번호가 일치합니다.'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            raise CustomValidation('-26', "비밀번호가 다릅니다.")

class ContentsPasswordDeleteAPI(APIView):
    """
      컨텐츠 비밀번호 삭제

    ---
    # /contents/password/delete
    """
    serializer_class = CommentSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user'],
            properties={
                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인시 전달받은 사용자 id 값'),
                'contents': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents id'),
            },
        ),
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
               'error': openapi.Schema(type=openapi.TYPE_INTEGER, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='컨텐츠 비밀번호가 삭제되었습니다.'),
                },
            ),
            400:
                error_collection.CONTENTS_HAS_NOT_USER.as_md() +
                error_collection.CONTENTS_PASSWORD_NOT_FOUND.as_md()
        },
    )
    def post(self, request, pk=None):

        #로그인 체크
        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        # 컨텐츠 여부 체크
        contents_pk = self.request.data.get('contents', None)
        contents = get_contents(contents_pk)

        if user != contents.user:
            raise CustomValidation('-20', '컨텐츠를 등록한 사용자가 아닙니다.')

        try:
            contents_password = ContentsPassword.objects.get(contents=contents)
            contents_password.delete()

            data = {
                "result": 1,
                "error": "null",
                "data": "컨텐츠 비밀번호가 삭제되었습니다."
            }

            return Response(data, status=status.HTTP_200_OK)
        except ContentsPassword.DoesNotExist:
            raise CustomValidation('-25', '등록된 비밀번호가 없습니다.')

class LikeAPI(APIView):
    """
    좋아요

    ---
    # /contents/like
    """

    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    serializer = serializer_class(queryset, many=True)

    @swagger_auto_schema( request_body=openapi.Schema(

        type=openapi.TYPE_OBJECT,
        required=['user', 'contents'],
        properties={
            'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인시 전달받은 사용자 id 값'),
            'contents': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents id')
        },
    ),
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1, 2'),
               'error': openapi.Schema(type=openapi.TYPE_STRING, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='좋아요 취소, 좋아요'),
                },
            ),
            400:
                error_collection.USERNAME_NOT_FOUND.as_md() +
                error_collection.CONTENTS_NOT_FOUNDS.as_md()
        },
    )
    def post(self, request, *args, **kwargs):

        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_contents(contents_pk)

        contents_like, contents_like_created = contents.like_set.get_or_create(user=user)

        if contents_like_created:
            data = {'result': 1, 'error': 'null', 'data': '좋아요'}
        else:
            data = {'result': 2,  'error': 'null', 'data': '좋아요 취소'}
            contents_like.delete()

        return Response(data, status=status.HTTP_200_OK)

class LikeCheckAPI(APIView):
    """
    로그인 유저의  "좋아요" 클릭 여부

    ---
    # /contents/like/check?user={user}&contents={contents}
    """

    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    serializer = serializer_class(queryset, many=True)

    @swagger_auto_schema(
        manual_parameters=[user, contents],
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0, 1'),
               'error': openapi.Schema(type=openapi.TYPE_STRING, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='좋아요를 클릭하지 않았습니다., 좋아요를 클릭했습니다.'),
                },
            ),
            400:
                error_collection.USERNAME_NOT_FOUND.as_md() +
                error_collection.CONTENTS_NOT_FOUNDS.as_md()
        },
    )

    def get(self, request, *args, **kwargs):

        user_pk = self.request.GET.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.GET.get('contents', None)
        contents = get_contents(contents_pk)

        try:
            Like.objects.get(contents=contents, user=user)
            data = {'result': 1, 'error': 'null', 'data': '좋아요를 클릭했습니다.'}
        except Like.DoesNotExist:
            data = {'result': 0, 'error': 'null', 'data': '좋아요를 클릭하지 않았습니다.'}

        return Response(data, status=status.HTTP_200_OK)


class UnLikeAPI(APIView):
    """
    싫어요

    ---
    # /contents/unlike
    """
    serializer_class = UnLikeSerializer
    queryset = UnLike.objects.all()
    serializer = serializer_class(queryset, many=True)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user', 'contents'],
            properties={
                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인시 전달받은 사용자 id 값'),
                'contents': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents id')
            },
        ),
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0, 1'),
               'error': openapi.Schema(type=openapi.TYPE_STRING, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='싫어요 취소, 싫어요'),
                },
            ),
            400:
                error_collection.USERNAME_NOT_FOUND.as_md() +
                error_collection.CONTENTS_NOT_FOUNDS.as_md()
        },
    )
    def post(self, request, *args, **kwargs):

        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_contents(contents_pk)

        contents_unlike, contents_unlike_created = contents.unlike_set.get_or_create(user=user)

        if contents_unlike_created:
            data = {'result': 1, 'error': 'null',  'data': '싫어요'}
        else:
            contents_unlike.delete()
            data = {'result': 0, 'error': 'null',  'data': '싫어요 취소'}

        return Response(data, status=status.HTTP_200_OK)

class UnLikeCheckAPI(APIView):
    """
    로그인 유저의  "싫어요" 클릭 여부

    ---
    # /contents/unlike/check?user={user}&contents={contents}
    """

    serializer_class = UnLikeSerializer
    queryset = UnLike.objects.all()
    serializer = serializer_class(queryset, many=True)

    @swagger_auto_schema(
        manual_parameters=[user, contents],
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0, 1'),
               'error': openapi.Schema(type=openapi.TYPE_STRING, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='싫어요를 클릭하지 않았습니다., 싫어요를 클릭했습니다.'),
                },
            ),
            400:
                error_collection.USERNAME_NOT_FOUND.as_md() +
                error_collection.CONTENTS_NOT_FOUNDS.as_md()
        },
    )

    def get(self, request, *args, **kwargs):

        user_pk = self.request.GET.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.GET.get('contents', None)
        contents = get_contents(contents_pk)

        try:
            UnLike.objects.get(contents=contents, user=user)
            data = {'result': 1, 'error': 'null', 'data': '싫어요를 클릭했습니다.'}
        except UnLike.DoesNotExist:
            data = {'result': 0, 'error': 'null', 'data': '싫어요를 클릭하지 않았습니다.'}

        return Response(data, status=status.HTTP_200_OK)


class CommentCreateAPI(CreateAPIView):
    """
    댓글 작성

    ---
    # /contents/comments/create?parent_id={parent_id}

    ## 내용
        - REQUEST BODY SCHEMA: application/json
         {
            "user" : 로그인시 전달받은 사용자 id 값,
            "contents" : contents id,
            "comment_content" : 댓글 내용
         }
        - RESPONSE SCHEMA 200: application/json
         {
            "result": 1,
            "error": null,
         }
        - RESPONSE SCHEMA 400: application/json
         {
            "result": "-8"
            "error": "존재하지 않는 ID 입니다."
            "data": "{}"
        }
        - RESPONSE SCHEMA 400: application/json
        {
            "result": "-17"
            "error": "등록된 컨텐츠가 없습니다."
            "data": "{}"
        }
        - RESPONSE SCHEMA 400: application/json
        {
            "result": "-31"
            "error": "댓글을 입력해주세요."
            "data": "{}"
        }
    """

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    @swagger_auto_schema(
        manual_parameters=[parent_id],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인시 전달받은 사용자 id 값'),
                'contents': openapi.Schema(type=openapi.TYPE_INTEGER, description='contents id'),
                'comment_content': openapi.Schema(type=openapi.TYPE_STRING, description='댓글'),
            }
        ),
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
               'error': openapi.Schema(type=openapi.TYPE_STRING, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='댓글이 등록되었습니다.'),
                },
            ),
            400:
                error_collection.USERNAME_NOT_FOUND.as_md() +
                error_collection.CONTENTS_NOT_FOUNDS.as_md()+
                error_collection.COMMENT_IS_BLANK.as_md()
        }
    )
    def get_serializer_class(self):
        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        get_contents(contents_pk)

        comment_content = self.request.data.get('comment_content', None)

        if comment_content is None:
                raise CustomValidation('-31', "댓글을 입력해주세요.")
        else:
            if len(comment_content) < 1:
                raise CustomValidation('-31', "댓글을 입력해주세요.")

        return create_comment_serializer(parent_id=self.request.GET.get("parent_id", None), user=user)


class CommentListAPI(APIView):
    
    """
    댓글 리스트

    ---
    # /contents/comments?user={user}&contents={contents}
    """
    serializer_class = CommentSerializer

    @swagger_auto_schema(
        manual_parameters=[user, contents],
        responses={
            200: CommentSerializer(),
            400:
                error_collection.USERNAME_NOT_FOUND.as_md() +
                error_collection.CONTENTS_NOT_FOUNDS.as_md()
        }
    )
    def get(self, *args, **kwargs):
        user_pk = self.request.GET.get('user', None)
        get_user(user_pk)

        contents_pk = self.request.GET.get("contents")
        get_contents(contents_pk)

        queryset = Comment.objects.filter(Q(contents=contents_pk) & Q(parent=None))
        serializer = self.serializer_class(queryset, many=True)
        data = {'result': 0, 'error': 'null', 'data': serializer.data}
        return Response(data)


class CommentDeleteAPI(APIView):

    """
    댓글 삭제

    ---
    # /contents/comments/delete/{id}
    """
    serializer_class = CommentSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user'],
            properties={
                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인시 전달받은 사용자 id 값'),
            },
        ),
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
               'error': openapi.Schema(type=openapi.TYPE_INTEGER, description='null'),
               'data': openapi.Schema(type=openapi.TYPE_STRING, description='삭제되었습니다.'),
                },
            ),
            400:
                error_collection.USERNAME_NOT_FOUND.as_md() +
                error_collection.COMMENT_DELETE_USER_NOT_MATCH.as_md() +
                error_collection.COMMENT_NOT_FOUNDS.as_md()
        },
    )
    def post(self, request, pk=None):

        user_pk = self.request.data.get('user', None)
        user= get_user(user_pk)

        comment = self.get_object(pk)

        if user.pk != comment.user.pk:
            raise CustomValidation('-27', '작성자만 삭제 가능합니다.')

        comment.delete()

        data = {
            "result": 1,
            "error": "null",
            "data": "댓글이 삭제되었습니다."
        }
        return Response(data, status=status.HTTP_200_OK)

    def get_object(self, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            return comment
        except Comment.DoesNotExist:
            raise CustomValidation('-28', '등록된 댓글이 없습니다.')

    def retrieve(self, request, pk=None):
        comment = self.get_object(pk)
        serializer = ContentsSerializer(comment)
        return Response(serializer.data)

 #   def put(self, request, pk=None):

        #       comment = get_object_or_404(Comment, pk=pk)

        #if request.user.pk != comment.user.pk:
        #    data = {"result": -2, "message": '작성자만 수정 가능합니다.'}
        #    raise serializers.ValidationError(data)

        #serializer = CommentSerializer(comment, data=request.data, partial=True)
        #if serializer.is_valid():
        #    serializer.save()
        #    data = {
        #        "result": 1,
        #        "data": serializer.data
        #    }
        #else:
        #    data = {
        #        "result": 0,
        #        "message": serializer.errors
        #    }

        #return Response(data, status=status.HTTP_200_OK)

