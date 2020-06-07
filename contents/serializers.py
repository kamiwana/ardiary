import json
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedIdentityField
from .models import *
from users.utils import get_user
from ardiary.exception_handler import CustomValidation

class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = '__all__'

class ContentsPasswordSerializer(serializers.ModelSerializer):

    def validate(self, value):
        password = value['password']
        if password is not None:
            if len(str(password)) != 4:
                raise CustomValidation('-22', "비밀번호는 4자리입니다.")
            elif password.isdigit() is False:
                raise CustomValidation('-23', "비밀번호는 숫자만 입력하세요.")
        return value

    class Meta:
        model = ContentsPassword
        fields = '__all__'

class UnLikeSerializer(serializers.Serializer):
    class Meta:
        model = UnLike

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveSerializer(many=True, read_only=True)

    def get_queryset(self):
        queryset = Comment.objects.filter(parent=None)
        return queryset

    class Meta:
        model = Comment
        fields = [
            'id',
            'username',
            'parent',
            'comment_content',
            'replies',
            'create_dt',
        ]

        read_only_fields = [
            'replies',
            'create_dt',
        ]

class CommentListSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='comments-api:thread')

    class Meta:
        model = Comment
        fields = [
            'url',
            'id',
            'comment_content',
            'create_date',
            'create_dt',
        ]

class ContentsFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentsFiles
        fields = '__all__'

class ContentsCreateFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentsFiles
        fields = '__all__'

    def create(self, validated_data):
        contentsfiles = ContentsFiles.objects.create(**validated_data)
        contents = validated_data.get("contents").pk    
        user = validated_data.get("user").pk
        for file_item in self.initial_data.getlist('file'):
            c = ContentsFiles(file=file_item, contents=contents, user=user)
            c.save()
        return contentsfiles

class ContentsCreateRequestSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(help_text="로그인시 전달받은 사용자 id 값")
    qr_data = serializers.CharField()
    activation_code = serializers.IntegerField(help_text="시리얼 번호")
    recog_type = serializers.IntegerField(required=False, help_text="1-이미지기반, 2-공간기반, 3-음성기반")
    link_01_type = serializers.IntegerField(required=False, help_text="1-페이스북, 2-사진, 3-쇼핑몰, 4-전화번호, "
                                                                      "5-카카오톡, 6-카카오톡, 7-유튜브, 8-기타 URL")
    link_02_type = serializers.IntegerField(required=False, help_text="1-페이스북, 2-사진, 3-쇼핑몰, 4-전화번호, "
                                                                      "5-카카오톡, 6-카카오톡, 7-유튜브, 8-기타 URL")
    effect_type = serializers.IntegerField(required=False, help_text="1-폭죽, 2-스노우, 3-선물상자")
    char_type = serializers.IntegerField(required=False, help_text="1-사람, 2-팬더")
    on_air = serializers.IntegerField(required=False, help_text="0-활성, 1-비활성")
    contents_files = serializers.FileField(required=False, help_text="이미지나 영상 데이터 여러장 가능")
    contents_files_type = serializers.CharField(required=False, help_text="1:영상, 2:이미지 - contents_files 갯수에 "
                                                                          "맞춰서 ',' 로 구분 (ex)1,2 ) ")
    class Meta:
        model = Contents
        fields = ('user', 'qr_data', 'activation_code', 'title', 'recog_type', 'video_url',
                  'label_text', 'neon_text', 'neon_style', 'neon_effect', 'neon_material', 'audio_url', 'link_01_type',
                  'link_01_url', 'link_02_type', 'link_02_url', 'effect_type', 'char_type', 'on_air', 'contents_files',
                  'contents_files_type'
                  )

class ContentsSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    qr_data = serializers.CharField(read_only=True)
    contents_comment = CommentSerializer(many=True, read_only=True)
    contents_files = ContentsFilesSerializer(many=True, read_only=True)

    class Meta:
        model = Contents
        fields = ('pk',  'qr_data', 'user', 'username', 'title', 'password', 'audio_url', 'recog_type',
                  'video_url', 'label_text', 'neon_text', 'neon_style', 'neon_effect', 'neon_material',
                  'link_01_type', 'link_01_url', 'link_02_type', 'link_02_url', 'effect_type', 'char_type','on_air',
                  'view_count', 'like_count','unlike_count', 'comment_count', 'update_dt',
                  'contents_comment', 'contents_files')
        read_only_fields = ('pk', 'update_dt', 'like_count', 'unlike_count', 'comment_count', 'username', 'qr_code',
                            'view_count')

    def create(self, validated_data):
        user = self._kwargs['data']['user']
        qr_data = self._kwargs['data']['qr_data']
        user = get_user(user)
        qr_data = QRDatas.objects.get(qr_data=qr_data)
        contents = Contents.objects.create(user=user, qr_data=qr_data,  **validated_data)
        QRDatas.objects.filter(pk=contents.qr_data.pk).update(is_active=1)

        contents_files = self.initial_data.getlist('contents_files')
        if len(contents_files) > 0:
            files_type = self.initial_data.getlist('contents_files_type')
            files_type_list = files_type[0].split(',')
            for file_item, file_type in zip(contents_files, files_type_list):
                c = ContentsFiles(file=file_item, file_type=file_type,  contents=contents,  user=contents.user)
                c.save()
            return contents

class ContentsUpdateRequestSerializer(serializers.ModelSerializer):

    recog_type = serializers.IntegerField(required=False, default=0, help_text="1-이미지기반, 2-공간기반, 3-음성기반")
    link_01_type = serializers.IntegerField(required=False, help_text="1-페이스북, 2-사진, 3-쇼핑몰, 4-전화번호, 5-카카오톡, 6-카카오톡, 7-유튜브, 8-기타 URL")
    link_02_type = serializers.IntegerField(required=False, help_text="1-페이스북, 2-사진, 3-쇼핑몰, 4-전화번호, 5-카카오톡, 6-카카오톡, 7-유튜브, 8-기타 URL")
    effect_type = serializers.IntegerField(required=False, help_text="1-폭죽, 2-스노우, 3-선물상자")
    char_type = serializers.IntegerField(required=False, help_text="1-사람, 2-팬더")
    on_air = serializers.IntegerField(required=False, help_text="0-활성, 1-비활성")
    contents_files = serializers.FileField(required=False, help_text="사진이나 이미지 데이터 여러장 가능")
    contents_files_type = serializers.CharField(required=False, help_text="1:영상, 2:이미지 - contents_files 갯수에 "
                                                                          "맞춰서 ',' 로 구분 (ex)1,2 ) ")
    class Meta:
        model = Contents
        fields = ('title', 'recog_type', 'video_url', 'label_text', 'neon_text',
                  'neon_style', 'neon_effect', 'neon_material', 'audio_url', 'link_01_type',
                  'link_01_url', 'link_02_type', 'link_02_url', 'effect_type', 'char_type', 'on_air', 'contents_files',
                  'contents_files_type'
                  )

class ContentsUpdateSerializer(serializers.ModelSerializer):
    contents_files = ContentsFilesSerializer(many=True, read_only=True)
    class Meta:
        model = Contents
        fields = ('pk', 'user',  'username',  'title',  'recog_type', 'video_url', 'label_text', 'neon_text',
                  'neon_style', 'neon_effect', 'neon_material', 'audio_url', 'link_01_type',
                  'link_01_url', 'link_02_type', 'link_02_url', 'effect_type', 'char_type','on_air', 'update_dt',
                  'contents_files')

    def update(self, instance, validated_data):
        contents_files = self.initial_data.getlist('contents_files')
        if len(contents_files) > 0:
            contents_files_db = ContentsFiles.objects.filter(contents_id=instance.id)
            contents_files_db.delete()
            files_type = self.initial_data.getlist('contents_files_type')
            files_type_list = files_type[0].split(',')
            for file_item, file_type in zip(contents_files, files_type_list):
                c = ContentsFiles(file=file_item, file_type=file_type,  contents=instance,  user=instance.user)
                c.save()

        instance.title = validated_data.get('title', instance.title)
        instance.recog_type = validated_data.get('recog_type', instance.recog_type)
        instance.label_text = validated_data.get('label_text', instance.label_text)
        instance.neon_text = validated_data.get('neon_text', instance.neon_text)
        instance.neon_style = validated_data.get('neon_style', instance.neon_style)
        instance.neon_material = validated_data.get('neon_material', instance.neon_material)
        instance.audio_url = validated_data.get('audio_url', instance.audio_url)
        instance.link_01_type = validated_data.get('link_01_type', instance.link_01_type)
        instance.link_01_url = validated_data.get('link_01_url', instance.link_01_url)
        instance.link_02_type = validated_data.get('link_02_type', instance.link_02_type)
        instance.link_02_url = validated_data.get('link_02_url', instance.link_02_url)
        instance.effect_type = validated_data.get('effect_type', instance.effect_type)
        instance.char_type = validated_data.get('char_type', instance.char_type)
        instance.on_air = validated_data.get('on_air', instance.on_air)


        instance.save()
        return instance

class ContentsRequestSerializer(serializers.ModelSerializer):
    contents_files = ContentsFilesSerializer(many=True)

    class Meta:
        model = Contents
        fields = ('title',  'recog_type', 'video_url', 'label_text', 'neon_text',
                  'neon_style', 'neon_effect', 'neon_material', 'audio_url', 'link_01_type',
                  'link_01_url', 'link_02_type', 'link_02_url', 'effect_type', 'char_type', 'on_air', 'contents_files')

class QRDatasSerializer(serializers.ModelSerializer):
    qrdatascontents = ContentsSerializer(read_only=True)

    class Meta:
        model = QRDatas
        fields = ('id', 'qr_data', 'is_active', 'activation_code', 'contents_type', 'create_dt', 'update_dt', 'qrdatascontents',)

def create_comment_serializer(parent_id=None, user=None):
    class CommentCreateSerializer(serializers.ModelSerializer):
        result = serializers.IntegerField(required=False,   default=1)
        error = serializers.CharField(max_length=5, required=False, default='null')

        class Meta:
            model = Comment
            fields = ('result', 'error', 'id', 'contents', 'parent', 'comment_content', 'create_dt')

        def __init__(self, *args, **kwargs):
            self.parent_obj = None
            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    self.parent_obj = parent_qs.first()
            return super(CommentCreateSerializer, self).__init__(*args, **kwargs)

        def create(self, validated_data):
            content = validated_data.get("comment_content")
            contents = validated_data.get("contents")
            parent_obj = self.parent_obj
            comment = Comment.objects.create(
                contents=contents,
                user=user,
                comment_content=content,
                parent=parent_obj
                    )

            return comment

    return CommentCreateSerializer
