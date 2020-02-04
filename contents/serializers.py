import json
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedIdentityField
from .models import *

class ContentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contents
        fields = '__all__'
        read_only_fields = ('pk', 'create_dt', 'update_dt')

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
        return contents

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

class CommentListSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='comments-api:thread')

    class Meta:
        model = Comment
        fields = [
            'url',
            'id',
            # 'content_type',
            # 'object_id',
            # 'parent',
            'comment_content',
            'create_date',
        ]

class SubcommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'comment_content', 'parent')


class CommentChildSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            'id',
            'comment_user_id',
            'parent',
            'comment_content',

        ]

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveSerializer(many=True, read_only=True)

    def get_queryset(self):
        user = self.context['request'].user
        queryset = Comment.objects.filter(parent=None)
        return queryset

    class Meta:
        model = Comment
        fields = [
            'id',
            'comment_user_id',
            'parent',
            'comment_content',
            'replies',
        ]

        read_only_fields = [
            'replies',
        ]