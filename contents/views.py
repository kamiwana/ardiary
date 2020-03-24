from rest_framework.generics import CreateAPIView
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.parsers import MultiPartParser
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

class ContentsList(APIView):

    parser_classes = (MultiPartParser,)
    serializer_class = ContentsSerializer
    queryset = Contents.objects.all()
    serializer = serializer_class(queryset, many=True)

    @swagger_auto_schema(request_body=ContentsSerializer)
    def post(self, request, *args, **kwargs):
        """
           컨텐츠를 작성하는 API

            ---
            # /contents/
            ## 내용
                - user :  로그인시 전달받은 사용자 id 값
                - recog_type : 0-이미지기반, 1-공간기반, 2-음성기반
                - link_01_type, link_02_type : 0-페이스북, 1-사진, 2-쇼핑몰, 3-전화번호, 4-카카오톡, 5-카카오톡, 6-유튜브, 7-기타URL
                - effect_type : 0-폭죽, 1-스노우, 2-선물상자
                - char_type : 0-사람, 1-팬더
                - contents_files : 사진이나 이미지 데이터 여러장 가능
        """

        data = request.data.copy()
        qr_data = data['qr_data']
        user = get_user(data['user'])

        try:
            qrdats = QRDatas.objects.get(qr_data=qr_data)

            if qrdats.is_active == 1:
                data = {"result": 0, "field": "qr_code", "qr_code": '컨텐츠가 등록된 QR코드 입니다.'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except QRDatas.DoesNotExist:
             data = {"qr_code": '등록된 QR코드가 없습니다.'}
             raise serializers.ValidationError(data)

        data['user'] = user.pk
        data['qr_data'] = qrdats.pk
        contents_serializer = ContentsSerializer(data=data)
        if contents_serializer.is_valid():
            contents_serializer.save()
            return Response(contents_serializer.data, status=status.HTTP_201_CREATED)
        else:
            data = {"contents": contents_serializer.errors}
            raise serializers.ValidationError(data)


class QRDataDetail(APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = QRDatasSerializer
    queryset = QRDatas.objects.all()

    @swagger_auto_schema(responses={
        200: openapi.Response('OK', QRDatasSerializer),
    })
    def get(self, request, user=None, qr_data=None):
        """
            QR코드로 특정 컨텐츠 데이터를 가져오는 API

            ---
            # /contents/qrdatas/{qr_data}
            ## 내용
                - recog_type : 0-이미지기반, 1-공간기반, 2-음성기반
                - link_01_type, link_02_type : 0-페이스북, 1-사진, 2-쇼핑몰, 3-전화번호, 4-카카오톡, 5-카카오톡, 6-유튜브, 7-기타URL
                - effect_type : 0-폭죽, 1-스노우, 2-선물상자
                - char_type : 0-사람, 1-팬더
                - contents_comment : 댓글 리스트
                - contents_files : 등록된 파일리스트
        """

        data = {"qr_code": '등록된 QR코드가 없습니다.'}
        try:
            qr_data = QRDatas.objects.get(qr_data=qr_data)
        except QRDatas.DoesNotExist:
            raise serializers.ValidationError(data)

        try:
            contents = Contents.objects.get(pk=qr_data.qrdatascontents.pk)
            contents.view_count = contents.view_count + 1
            contents.save()

            serializer = self.serializer_class(qr_data)
            return Response(serializer.data)
        except:
            data = {"contents": '등록된 컨텐츠가 없습니다.'}
            raise serializers.ValidationError(data)


class QRDataDetail(APIView):

    parser_classes = (MultiPartParser,)
    serializer_class = QRDatasSerializer
    queryset = QRDatas.objects.all()

    @swagger_auto_schema(responses={
        200: openapi.Response('OK', QRDatasSerializer),
    })

    def get(self, request, user=None, qr_data=None):
        """
            QR코드로 특정 컨텐츠 데이터를 가져오는 API

            ---
            # /contents/qrdatas/{qr_data}
            ## 내용
                - recog_type : 0-이미지기반, 1-공간기반, 2-음성기반
                - link_01_type, link_02_type : 0-페이스북, 1-사진, 2-쇼핑몰, 3-전화번호, 4-카카오톡, 5-카카오톡, 6-유튜브, 7-기타URL
                - effect_type : 0-폭죽, 1-스노우, 2-선물상자
                - char_type : 0-사람, 1-팬더
                - contents_comment : 댓글 리스트
                - contents_files : 등록된 파일리스트
        """

        data = {"qr_code": '등록된 QR코드가 없습니다.'}
        try:
            qr_data = QRDatas.objects.get(qr_data=qr_data)
        except QRDatas.DoesNotExist:
            raise serializers.ValidationError(data)
        
        try:
            contents = Contents.objects.get(pk=qr_data.qrdatascontents.pk)
            contents.view_count = contents.view_count + 1
            contents.save()

            serializer = self.serializer_class(qr_data)
            return Response(serializer.data)
        except:
            data = {"contents": '등록된 컨텐츠가 없습니다.'}
            raise serializers.ValidationError(data)


class ContentsDetail(APIView):

    parser_classes = (MultiPartParser,)
    serializer_class = ContentsSerializer
    queryset = Contents.objects.all()


    def get_object(self, pk, user):
        data = {"contents": '해당 컨텐츠가 없습니다.'}
        try:
            contents = Contents.objects.get(pk=pk)

            if user == contents.user:
                return contents
            else:
                raise serializers.ValidationError(data)
        except Contents.DoesNotExist:
            raise serializers.ValidationError(data)

    @swagger_auto_schema(manual_parameters=[user], responses={
        200: openapi.Response('OK', ContentsSerializer),
    })
    def get(self, request,  pk=None):
        """
            컨텐츠에서 특정 id를 가지는 데이터를 가져오는 API

            ---
            # /contents/{id}?user={user}
            ## 내용
                - recog_type : 0-이미지기반, 1-공간기반, 2-음성기반
                - link_01_type, link_02_type : 0-페이스북, 1-사진, 2-쇼핑몰, 3-전화번호, 4-카카오톡, 5-카카오톡, 6-유튜브, 7-기타URL
                - effect_type : 0-폭죽, 1-스노우, 2-선물상자
                - char_type : 0-사람, 1-팬더
                - contents_comment : 댓글 리스트
                - contents_files : 등록된 사진이나 이미지 데이터 리스트
        """
        user_pk = self.request.GET.get("user", None)
        user = get_user(user_pk)

        try:
            contents = Contents.objects.get(pk=pk)
            contents.view_count = contents.view_count + 1
            contents.save()

            serializer = self.serializer_class(contents)
            return Response(serializer.data)

        except:
            data = {"contents": '해당 컨텐츠가 없습니다.'}
            raise serializers.ValidationError(data)

        #   def post(self, request, pk=None):
        """
            컨텐츠에서 특정 id의 내용 수정

            ---
            # /contents/{id}?user={user}
            ## 내용
                - user :  로그인시 전달받은 사용자 id 값

                - recog_type : 0-이미지기반, 1-공간기반, 2-음성기반
                - link_01_type, link_02_type : 0-페이스북, 1-사진, 2-쇼핑몰, 3-전화번호, 4-카카오톡, 5-카카오톡, 6-유튜브, 7-기타URL
                - effect_type : 0-폭죽, 1-스노우, 2-선물상자
                - char_type : 0-사람, 1-팬더
                - contents_comment : 댓글 리스트
                - contents_files : 등록된 사진이나 이미지 데이터 리스트
        """
        #        user_pk = self.request.GET.get("user", None)
        #        user = get_user(user_pk)

        #        contents = get_object_or_404(Contents, pk=pk)

        #        if user.pk != contents.user.pk:
        #            data = {"contents": "  작성자만 수정 가능합니다."}
        #            raise serializers.ValidationError(data)

        #        serializer = ContentsSerializer(contents, data=request.data, partial=True)
        #        if serializer.is_valid():
        #            serializer.save()
        #            return Response(serializer.data, status=status.HTTP_200_OK)
        #        else:
        #            data = {"contents": serializer.errors}
        #            raise serializers.ValidationError(data)


#   def delete(self, request, pk=None):

# queryset = get_object_or_404(Contents, pk=pk)
# queryset.delete()
# data = {"result": 1, "message": "success"}
# return Response(data, status=status.HTTP_200_OK)


class Like(APIView):
    """
    "좋아요" - 컨텐츠에서 특정 id를 가지는 데이터
    ---
    # /contents/like
    """

    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    serializer = serializer_class(queryset, many=True)

    @swagger_auto_schema(request_body=openapi.Schema(

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
            data = {'result': 1, 'message': '좋아요'}
        else:
            data = {'result': 0, 'message': '좋아요 취소'}
            contents_like.delete()

        return Response(data, status=status.HTTP_200_OK)

class UnLike(APIView):
    """
   "싫어요" - 컨텐츠에서 특정 id를 가지는 데이터

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
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='싫어요 취소, 싫어요'),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        user_pk = self.request.data.get('user', None)
        user = get_user(user_pk)

        contents_pk = self.request.data.get('contents', None)
        contents = get_object_or_404(Contents, pk=contents_pk)
        contents_unlike, contents_unlike_created = contents.unlike_set.get_or_create(user=user)

        if contents_unlike_created:
            data = {'result': 1, 'message': '싫어요'}
        else:
            contents_unlike.delete()
            data = {'result': 0, 'message': '싫어요 취소'}

        return Response(data, status=status.HTTP_200_OK)

class CommentCreateAPIView(CreateAPIView):
    """
    댓글 작성  API

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

class CommentList(APIView):
    
    """
    특정 글의  댓글 리스트
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

class CommentDelete(APIView):

    """
    댓글 삭제  API
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
               'message': openapi.Schema(type=openapi.TYPE_STRING, description='삭제되었습니다.'),
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

