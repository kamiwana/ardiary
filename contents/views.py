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
             status.HTTP_200_OK: openapi.Response('OK', QRDatasSerializer),
             status.HTTP_400_BAD_REQUEST: openapi.Schema(
                 type=openapi.TYPE_OBJECT,
                 properties={
                     'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0'),
                     'field': openapi.Schema(type=openapi.TYPE_INTEGER,
                                             description='qr_code, activation_code, contents'),
                     'message': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='등록된 QR코드가 없습니다. 등록된 시리얼 번호가 없습니다. '
                                                           '컨텐츠가 등록된 QR코드 입니다.'),
                     },
                 ),
             },
         )
    def post(self, request, *args, **kwargs):
        """
           컨텐츠 작성

            ---
            # /contents/

        """

        user = get_user(request.data['user'])

        qr_data = request.data['qr_data']
        activation_code = request.data['activation_code']

        try:
            qrdats = QRDatas.objects.get(qr_data=qr_data)

            data = {"activation_code": '등록된 시리얼 번호가 없습니다.'}
            if activation_code:
                if str(qrdats.activation_code) != activation_code:
                    raise serializers.ValidationError(data)
            else:
                raise serializers.ValidationError(data)

            if qrdats.is_active == 1:
                data = {"contents": '컨텐츠가 등록된 QR코드 입니다.'}
                raise serializers.ValidationError(data)

        except QRDatas.DoesNotExist:
             data = {"qr_code": '등록된 QR코드가 없습니다.'}
             raise serializers.ValidationError(data)

        data = request.data.copy()
        data['user'] = user.pk
        data['qr_data'] = qrdats.pk
        contents_serializer = ContentsSerializer(data=data)
        if contents_serializer.is_valid():
            contents_serializer.save()
            return Response(contents_serializer.data, status=status.HTTP_201_CREATED)
        else:
            data = {"contents": contents_serializer.errors}
            raise serializers.ValidationError(data)


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
             status.HTTP_200_OK: openapi.Response('OK', ContentsUpdateSerializer),
             status.HTTP_400_BAD_REQUEST: openapi.Schema(
                 type=openapi.TYPE_OBJECT,
                 properties={
                     'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0'),
                     'field': openapi.Schema(type=openapi.TYPE_INTEGER,
                                             description='contents'),
                     'message': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='작성자만 수정 가능합니다.'),
                     },
                 ),
             },
         )
    def post(self, request, pk=None, user=None):

        user = get_user(user)
        data = request.data.copy()
        data['user'] = user.pk

        queryset = get_object_or_404(Contents, pk=pk)

        if user.pk != queryset.user.pk:
            data = {"contents": '작성자만 수정 가능합니다.'}
            raise serializers.ValidationError(data)

        contents_serializer = ContentsUpdateSerializer(queryset, data=request.data, partial=True)

        if contents_serializer.is_valid():
            contents_serializer.save()
            return Response(contents_serializer.data, status=status.HTTP_200_OK)
        else:
            data = {"contents": contents_serializer.errors}
            raise serializers.ValidationError(data)


class QRDataDetailAPI(APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = QRDatasSerializer
    queryset = QRDatas.objects.all()

    @swagger_auto_schema(manual_parameters=[activation_code],
        responses={
            status.HTTP_200_OK: openapi.Response('OK', QRDatasSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0'),
                    'field': openapi.Schema(type=openapi.TYPE_INTEGER, description='qr_code, activation_code, contents'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING,
                        description='등록된 QR코드가 없습니다. 등록된 시리얼 번호가 다릅니다. 등록된 컨텐츠가 없습니다.'),
                },
            ),
    })
    def get(self, request, qr_data=None):
        """
            QR코드, 시리얼번호 체크 , 컨텐츠 가져오기

            ---
            # /contents/qrdatas/{qr_data}?activation_code={activation_code}
            ## 내용
                - recog_type : 0-이미지기반, 1-공간기반, 2-음성기반
                - link_01_type, link_02_type : 0-페이스북, 1-사진, 2-쇼핑몰, 3-전화번호, 4-카카오톡, 5-카카오톡, 6-유튜브, 7-기타URL
                - effect_type : 0-폭죽, 1-스노우, 2-선물상자
                - char_type : 0-사람, 1-팬더
                - contents_comment : 댓글 리스트
                - contents_files : 등록된 파일리스트
        """

        try:
            qr_data = QRDatas.objects.get(qr_data=qr_data)
        except QRDatas.DoesNotExist:
            data = {"qr_code": '등록된 QR코드가 없습니다.'}
            raise serializers.ValidationError(data)

        activation_code = self.request.GET.get("activation_code")
        if activation_code:
            if str(qr_data.activation_code) != activation_code:
                data = {"activation_code": '등록된 시리얼 번호가 다릅니다.'}
                raise serializers.ValidationError(data)
        try:
            contents = Contents.objects.get(pk=qr_data.qrdatascontents.pk)
            contents.view_count = contents.view_count + 1
            contents.save()

            serializer = self.serializer_class(qr_data)
            return Response(serializer.data)
        except:
            data = {
                "result": 0,
                "field": "contents",
                "message": "등록된 컨텐츠가 없습니다.",
                "qr_data": qr_data.qr_data,
                "activation_code": qr_data.activation_code,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class ContentsPasswordCreateAPI(APIView):
    """
    컨텐츠 패스워드  설정

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
                'field': openapi.Schema(type=openapi.TYPE_INTEGER, description='password'),
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='패스워드가 설정되었습니다.'),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)

        if user != contents.user:
            data = {"user": "컨텐츠 등록한 사용자가 아닙니다."}
            raise serializers.ValidationError(data)

        contents_password_serializer = ContentsPasswordSerializer(data=request.data)
        if contents_password_serializer.is_valid():
            contents_password_serializer.save()
            data = {'result': 1, 'field': 'password', 'message': '패스워드가 설정되었습니다.'}
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = {"passowrd": contents_password_serializer.errors}
            raise serializers.ValidationError(data)

class ContentsPasswordUpdateAPI(APIView):
    """
    컨텐츠 패스워드 수정

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
            status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
                'field': openapi.Schema(type=openapi.TYPE_INTEGER, description='password'),
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='패스워드가 수정되었습니다.'),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)

        if user != contents.user:
            data = {"user": "컨텐츠 등록한 사용자가 아닙니다."}
            raise serializers.ValidationError(data)

        queryset = get_object_or_404(ContentsPassword, contents=contents)

        contents_password_serializer = ContentsPasswordSerializer(queryset, data=request.data, partial=True)
        if contents_password_serializer.is_valid():
            contents_password_serializer.save()
            data = {'result': 1, 'field': 'password', 'message': '패스워드가 수정되었습니다.'}
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = {"passowrd": contents_password_serializer.errors}
            raise serializers.ValidationError(data)

class ContentsPasswordAPI(APIView):
    """
    컨텐츠 패스워드 확인

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
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                   'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
                   'field': openapi.Schema(type=openapi.TYPE_INTEGER, description='password'),
                   'message': openapi.Schema(type=openapi.TYPE_STRING, description='패스워드가  일치합니다.'),
                    },
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0'),
                    'field': openapi.Schema(type=openapi.TYPE_INTEGER, description='password'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='패스워드가 다릅니다.'),
                }
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        #로그인 체크
        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        # 컨텐츠 여부 체크
        contents_pk = self.request.data.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)

        # 패스워드 체크
        contents_password = self.request.data.get('password', None)

        if contents_password == contents.contentspassword.password:
            data = {'result': 1, 'field': 'password', 'message': '패스워드가 일치합니다.'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'password': '패스워드가 다릅니다.'}
            raise serializers.ValidationError(data)

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
            status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0, 1'),
               'field': openapi.Schema(type=openapi.TYPE_STRING, description='like'),
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='좋아요 취소, 좋아요'),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)
        contents_like, contents_like_created = contents.like_set.get_or_create(user=user)

        if contents_like_created:
            data = {'result': 1, 'field': 'like', 'message': '좋아요'}
        else:
            data = {'result': 0,  'field': 'like', 'message': '좋아요 취소'}
            contents_like.delete()

        return Response(data, status=status.HTTP_200_OK)


    def get(self, request, *args, **kwargs):

        user_pk = self.request.GET.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.GET.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)

        try:
            Like.objects.get(contents=contents, user=user)
            data = {'result': 1, 'field': 'like', 'message': '좋아요를 클릭했습니다.'}
        except Like.DoesNotExist:
            data = {'result': 0, 'field': 'like', 'message': '좋아요를 클릭하지 않았습니다.'}

        return Response(data, status=status.HTTP_200_OK)

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
            status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0, 1'),
               'field': openapi.Schema(type=openapi.TYPE_STRING, description='like'),
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='좋아요 취소, 좋아요'),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)
        contents_like, contents_like_created = contents.like_set.get_or_create(user=user)

        if contents_like_created:
            data = {'result': 1, 'field': 'like', 'message': '좋아요'}
        else:
            data = {'result': 0,  'field': 'like', 'message': '좋아요 취소'}
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
            status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0, 1'),
               'field': openapi.Schema(type=openapi.TYPE_STRING, description='like'),
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='좋아요를 클릭하지 않았습니다., 좋아요를 클릭했습니다.'),
                },
            ),
        },
    )

    def get(self, request, *args, **kwargs):

        user_pk = self.request.GET.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.GET.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)

        try:
            Like.objects.get(contents=contents, user=user)
            data = {'result': 1, 'field': 'like', 'message': '좋아요를 클릭했습니다.'}
        except Like.DoesNotExist:
            data = {'result': 0, 'field': 'like', 'message': '좋아요를 클릭하지 않았습니다.'}

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
            status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0, 1'),
               'field': openapi.Schema(type=openapi.TYPE_STRING, description='unlike'),
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='싫어요 취소, 싫어요'),
                },
            )
        },
    )
    def post(self, request, *args, **kwargs):

        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)
        contents_unlike, contents_unlike_created = contents.unlike_set.get_or_create(user=user)

        if contents_unlike_created:
            data = {'result': 1, 'field': 'unlike',  'message': '싫어요'}
        else:
            contents_unlike.delete()
            data = {'result': 0, 'field': 'unlike',  'message': '싫어요 취소'}

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
            status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0, 1'),
               'field': openapi.Schema(type=openapi.TYPE_STRING, description='unlike'),
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='싫어요를 클릭하지 않았습니다., 싫어요를 클릭했습니다.'),
                },
            )
        },
    )

    def get(self, request, *args, **kwargs):

        user_pk = self.request.GET.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.GET.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)

        try:
            UnLike.objects.get(contents=contents, user=user)
            data = {'result': 1, 'field': 'unlike', 'message': '싫어요를 클릭했습니다.'}
        except UnLike.DoesNotExist:
            data = {'result': 0, 'field': 'unlike', 'message': '싫어요를 클릭하지 않았습니다.'}

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
        - RESPONSE SCHEMA: application/json
         {
            "id": 댓글 id,
            "contents": contents id,
            "parent": 상위 댓글 id,
            "comment_content":  댓글 내용,
            "create_dt": 작성일
         }
    """

    serializer_class = CommentSerializer

    @swagger_auto_schema(
        manual_parameters=[parent_id],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'contents': openapi.Schema(type=openapi.TYPE_INTEGER, description='integer'),
                'comment_content': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            }
        ),
        responses={200: CommentSerializer()}
    )
    def get_serializer_class(self):
        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        get_object_or_404(Contents, pk=self.request.data.get("contents"))
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
        responses={200: CommentSerializer()}
    )
    def get(self, *args, **kwargs):
        user_pk = self.request.GET.get('user', None)
        get_user(user_pk)

        contents = self.request.GET.get("contents")
        queryset = Comment.objects.filter(Q(contents=contents) & Q(parent=None))
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

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
            status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
               'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='1'),
               'field': openapi.Schema(type=openapi.TYPE_INTEGER, description='comments'),
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='삭제되었습니다.'),
                },
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='0'),
                    'field': openapi.Schema(type=openapi.TYPE_INTEGER, description='comments'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='작성자만 삭제 가능합니다.'),
                },
            ),
        },
    )
    def post(self, request, pk=None):

        user_pk = self.request.data.get('user', None)
        user= get_user(user_pk)

        comment = self.get_object(pk)

        if user.pk != comment.user.pk:
            data = {'comments': '작성자만 삭제 가능합니다.'}
            raise serializers.ValidationError(data)

        comment.delete()

        data = {
            "result": 1,
            "field": "comments",
            "message": "삭제되었습니다."
        }
        return Response(data, status=status.HTTP_200_OK)

    def get_object(self, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            return comment
        except Comment.DoesNotExist:
            raise Http404

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

