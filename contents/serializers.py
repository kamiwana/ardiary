import json
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedIdentityField
from .models import *

class LikeSerializer(serializers.Serializer):
    class Meta:
        model = Like

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
        ]

        read_only_fields = [
            'replies',
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
        ]

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentsFiles
        fields = '__all__'

class ContentsSerializer(serializers.ModelSerializer):
  #  user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    contents_comment = CommentSerializer(many=True, read_only=True)
    contents_files = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Contents
        fields = ('pk', 'user', 'qr_data', 'qr_code', 'title', 'recog_type', 'password', 'video_url', 'label_text', 'neon_text',
                  'neon_style', 'neon_effect', 'neon_material', 'audio_url', 'link_01_type',
                  'link_01_url', 'link_02_type', 'link_02_url', 'effect_type', 'char_type', 'view_count',
                  'like_count', 'comment_count', 'update_dt', 'username', 'contents_comment', 'contents_files')
        read_only_fields = ('pk', 'update_dt', 'like_count', 'comment_count', 'username', 'qr_code',)

    def validate_qr_data(self, value):
        try:
            qr_data = QRDatas.objects.get(qr_data=value)
            if qr_data.is_active == 1:
                raise serializers.ValidationError('QR코드가 이미 사용되었습니다.')
            else:
                return qr_data
        except QRDatas.DoesNotExist:
            raise serializers.ValidationError('등록된 QR코드가 없습니다.')

    def validate_password(self, value):
        if value is not None:
            if len(str(value)) != 4:
                raise serializers.ValidationError("비밀번호는 4자리입니다.")
        return value

    def validate_photo_image(self, value):
        if value is None:
            data = {"contents": 'photo_image 가 없습니다.'}
            raise serializers.ValidationError(data)
        return value


    def create(self, validated_data):
        contents = Contents.objects.create(**validated_data)
        QRDatas.objects.filter(pk=contents.qr_data.pk).update(is_active=1)

        for file_item in self.initial_data.getlist('contents_files'):
            c = ContentsFiles(file=file_item, contents=contents, user=contents.user)
            c.save()
        return contents

    def update(self, instance, validated_data):
      for item in validated_data:
          if Contents._meta.get_field(item):
              setattr(instance, item, validated_data[item])

      c = ContentsFiles(file=self.context['request'].FILES['contents_files'], contents=instance)
      c.save()

      instance.save()
      setattr(instance, '_prefetched_objects_cache', True)
      return instance

class QRDatasSerializer(serializers.ModelSerializer):
    qrdatascontents = ContentsSerializer(read_only=True)

    class Meta:
        model = QRDatas
        fields = ('id', 'qr_data', 'is_active', 'activation_code', 'create_dt', 'update_dt', 'qrdatascontents',)

def create_comment_serializer(parent_id=None, user=None):
    class CommentCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = [
                'id',
                'contents',
                'parent',
                'comment_content',
                'create_dt',
            ]
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
                parent=parent_obj,
                    )

            return comment
    return CommentCreateSerializer
